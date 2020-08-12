#!/usr/bin/python3
import json
import pika
import os
import time


def start_studio(ch, method, properties, body):
    print(str(json.loads(body)))


def start_announce(ch, method, properties, body):
    print(str(json.loads(body)))


def start_rabiea(ch, method, properties, body):
    print(str(json.loads(body)))


def start_rabiea_480(ch, method, properties, body):
    print(str(json.loads(body)))


def start_rabiea_sizeless(ch, method, properties, body):
    print(str(json.loads(body)))


def digest(ch, method, properties, body):
    message = json.loads(body)
    if message['tag'] == 'studio':
        start_studio(ch, method, properties, body)
    elif message['tag'] == 'start_announce':
        start_announce(ch, method, properties, body)
    elif message['tag'] == 'rabiea':
        start_rabiea(ch, method, properties, body)
    elif message['tag'] == 'rabiea-480':
        start_rabiea_480(ch, method, properties, body)
    elif message['tag'] == 'rabiea-sizeless':
        start_rabiea_sizeless(ch, method, properties, body)
    else:
        print('Unknown tag context ... ->' + message)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def initialize():
    # host = 'localhost'
    # host = '192.168.0.4'
    host = '192.168.5.36'
    queue_name = 'studio-app'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=digest, auto_ack=False)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    initialize()
