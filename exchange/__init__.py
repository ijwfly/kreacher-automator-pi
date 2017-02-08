import pika
import json
import threading
import uuid


class Event(object):

    registered_events = {}

    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Event):
                obj_dict = {"name": type(obj).__name__}
                obj_dict.update(obj.__dict__)
                return obj_dict
            else:
                json.JSONEncoder.default(self, obj)

    class JSONDecoder(json.JSONDecoder):
        def decode(self, obj):
            obj_dict = json.loads(obj)

            if "name" not in obj_dict:
                raise TypeError

            event_name = obj_dict["name"]
            del(obj_dict["name"])

            if event_name in Event.registered_events:
                return Event.registered_events[event_name](**obj_dict)
            else:
                return Event(event_name)

    def __init__(self):
        self.name = type(self).__name__

    def is_an(self, event_class):
        return type(self).__name__ == event_class.__name__

    @staticmethod
    def register_event(event_class):
        Event.registered_events[event_class.__name__] = event_class
        return event_class


def message_handler(callback):
    def handler(ch, method, properties, body):
        decoder = Event.JSONDecoder()
        event = decoder.decode(body.decode("utf-8"))
        response = callback(event)
        if response:
            response_json = json.dumps(response, cls=Event.JSONEncoder)
            ch.basic_publish(exchange='',
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=response_json)
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
            decoder = Event.JSONDecoder()
            event = decoder.decode(body.decode("utf-8"))

            self.response_callbacks[properties.correlation_id](event)
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
        event_json = json.dumps(event, cls=Event.JSONEncoder)
        properties = None
        if response_callback:
            properties = self._add_response_callback(response_callback)
        self.channel.basic_publish(exchange='frontend', routing_key='',
                                   body=event_json, properties=properties)

    def publish_to_backend(self, subscriber_name, event, response_callback=None):
        event_json = json.dumps(event, cls=Event.JSONEncoder)
        properties = None
        if response_callback:
            properties = self._add_response_callback(response_callback)
        self.channel.basic_publish(exchange='backend', routing_key=subscriber_name,
                                   body=event_json, properties=properties)

    def wait_for_messages(self, non_blocking=True):
        if non_blocking:
            self.consume_thread = threading.Thread(target=self.channel.start_consuming)
            self.consume_thread.start()
        else:
            self.channel.start_consuming()
