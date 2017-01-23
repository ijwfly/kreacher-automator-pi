import pika
import json
import threading


class Event(object):
    def __init__(self, name, sender=None, data=None):
        self.name = name
        self.sender = sender
        self.data = data

    def __str__(self):
        return self.sender + ": [" + self.name + "] " + self.data;


def message_handler(callback):
    def handler(ch, method, properties, body):
        event_dict = json.loads(body.decode("utf-8"))
        if 'sender' in event_dict and 'name' in event_dict and 'data' in event_dict:
            callback(Event(**event_dict))
        else:
            raise "can't parse event dict"
    return handler


class Messenger(object):
    def __init__(self, message_broker_host):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=message_broker_host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='frontend', type='fanout')
        self.channel.exchange_declare(exchange='backend', type='direct')
        self.thread = None

    def subscribe_frontend(self, callback):
        queue = self.channel.queue_declare(exclusive=True).method.queue
        self.channel.queue_bind(exchange='frontend', queue=queue)
        self.channel.basic_consume(message_handler(callback), queue=queue, no_ack=True)

    def subscribe_backend(self, subscriber_name, callback):
        queue = self.channel.queue_declare(exclusive=True).method.queue
        self.channel.queue_bind(exchange='backend', queue=queue, routing_key=subscriber_name)
        self.channel.basic_consume(message_handler(callback), queue=queue, no_ack=True)

    def publish_to_frontend(self, event):
        event_json = json.dumps(event, default=lambda o: o.__dict__)
        self.channel.basic_publish(exchange='frontend', routing_key='', body=event_json)

    def publish_to_backend(self, subscriber_name, event):
        event_json = json.dumps(event, default=lambda o: o.__dict__)
        self.channel.basic_publish(exchange='backend', routing_key=subscriber_name, body=event_json)

    def wait_for_messages(self, non_blocking=True):
        if non_blocking:
            self.thread = threading.Thread(target=self.channel.start_consuming)
            self.thread.start()
        else:
            self.channel.start_consuming()
