import pika
import json
import threading
import uuid


class Event(object):
    def __init__(self, name, sender=None, data=None):
        self.name = name
        self.sender = sender
        self.data = data

    def __str__(self):
        return self.sender + ": [" + self.name + "] " + self.data

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @staticmethod
    def from_json(event_json):
        event_dict = json.loads(event_json)
        if 'sender' in event_dict and 'name' in event_dict and 'data' in event_dict:
            return Event(**event_dict)
        else:
            raise "can't parse event dict"


def message_handler(callback):
    def handler(ch, method, properties, body):
        event = Event.from_json(body.decode("utf-8"))
        response = callback(event)
        if response:
            ch.basic_publish(exchange='',
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=response.json())
    return handler


class Messenger(object):
    def __init__(self, message_broker_host):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=message_broker_host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='frontend', type='fanout')
        self.channel.exchange_declare(exchange='backend', type='direct')

        self.response_queue = self.channel.queue_declare(exclusive=True).method.queue
        self.response_callbacks = {}
        self.channel.basic_consume(self._process_response, no_ack=True, queue=self.response_queue)

        self.consume_thread = None

    def _process_response(self, ch, method, properties, body):
        if properties.correlation_id in self.response_callbacks:
            self.response_callbacks[properties.correlation_id](Event.from_json(body.decode("utf-8")))
            del(self.response_callbacks[properties.correlation_id])

    def _add_response_callback(self, callback):
        correlation_id = str(uuid.uuid4())
        self.response_callbacks[correlation_id] = callback
        return pika.BasicProperties(
            reply_to=self.response_queue,
            correlation_id=str(correlation_id)
        )

    def subscribe_frontend(self, callback):
        queue = self.channel.queue_declare(exclusive=True).method.queue
        self.channel.queue_bind(exchange='frontend', queue=queue)
        self.channel.basic_consume(message_handler(callback), queue=queue, no_ack=True)

    def subscribe_backend(self, subscriber_name, callback):
        queue = self.channel.queue_declare(exclusive=True).method.queue
        self.channel.queue_bind(exchange='backend', queue=queue, routing_key=subscriber_name)
        self.channel.basic_consume(message_handler(callback), queue=queue, no_ack=True)

    def publish_to_frontend(self, event, response_callback=None):
        properties = None
        if response_callback:
            properties = self._add_response_callback(response_callback)
        self.channel.basic_publish(exchange='frontend', routing_key='',
                                   body=event.json(), properties=properties)

    def publish_to_backend(self, subscriber_name, event, response_callback=None):
        properties = None
        if response_callback:
            properties = self._add_response_callback(response_callback)
        self.channel.basic_publish(exchange='backend', routing_key=subscriber_name,
                                   body=event.json(), properties=properties)

    def wait_for_messages(self, non_blocking=True):
        if non_blocking:
            self.consume_thread = threading.Thread(target=self.channel.start_consuming)
            self.consume_thread.start()
        else:
            self.channel.start_consuming()
