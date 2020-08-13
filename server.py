#!/usr/bin/python3
import json
import subprocess
import pika
import os
import shutil
import time


def start_studio(message):
    print(str(message))


def start_announce(message):
    print(message)
    print('start_announce ...')
    for folder in [item.name for item in os.scandir(PATH_ANNOUNCE) if item.is_dir()]:
        if os.path.isdir(os.path.join(PATH_ANNOUNCE, folder, PATH_HIGH)):
            if not os.path.exists(os.path.join(PATH_ANNOUNCE, folder, PATH_MID)):
                os.makedirs(os.path.join(PATH_ANNOUNCE, folder, PATH_MID))
            if not os.path.exists(os.path.join(PATH_ANNOUNCE, folder, PATH_LOW)):
                os.makedirs(os.path.join(PATH_ANNOUNCE, folder, PATH_LOW))
            for file in [item.name for item in os.scandir(os.path.join(PATH_ANNOUNCE, folder, PATH_HIGH)) if
                         item.is_file()]:
                if file.endswith(('.mp4', '.MP4')):
                    in_high = os.path.join(PATH_ANNOUNCE, folder, PATH_HIGH, file)
                    out_mid = os.path.join(PATH_ANNOUNCE, folder, PATH_MID, file)
                    out_low = os.path.join(PATH_ANNOUNCE, folder, PATH_LOW, file)
                    command = 'ffmpeg -y -i \"' + in_high + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 854x854 -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart \"' + out_mid + '\"  -threads 11 -sws_flags lanczos  -s 426x426 -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 50k -movflags +faststart \"' + out_low + '\"  -threads 11'
                    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                    process.wait()
            shutil.move(os.path.join(PATH_ANNOUNCE, folder), os.path.join(PATH_ANNOUNCE, 'done', folder))
    print('start_announce done')


def start_rabiea(message):
    print(str(message))


def start_rabiea_480(message):
    print(str(message))


def start_rabiea_sizeless(message):
    print(str(message))


def digest(ch, method, properties, body):
    message = json.loads(body)
    if message['tag'] == 'studio':
        start_studio(message)
    elif message['tag'] == 'announce':
        start_announce(message)
    elif message['tag'] == 'rabiea':
        start_rabiea(message)
    elif message['tag'] == 'rabiea-480':
        start_rabiea_480(message)
    elif message['tag'] == 'rabiea-sizeless':
        start_rabiea_sizeless(message)
    else:
        print('Unknown tag context ... ->' + message)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def listen():
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
    PATH_ANNOUNCE = '/home/film/announce'
    PATH_CONVERT = '/home/film/convert'

    PATH_HIGH = 'HD_720p'
    PATH_MID = 'hq'
    PATH_LOW = '240p'

    listen()
