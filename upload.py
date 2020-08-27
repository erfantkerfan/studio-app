import base64
import json
import os
import shutil
import subprocess
import time

import pika
import termcolor
from dotenv import load_dotenv


def start_normal(message):
    path_studio = os.path.join(PATH_NORMAL, message['ip'])
    print(termcolor.colored('start_normal ...' + get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --size-only \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_NORMAL
    run_command(command, path_studio)


def start_normal_force(message):
    path_studio = os.path.join(PATH_NORMAL_FORCE, message['ip'])
    print(termcolor.colored('start_normal_force ...' + get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --ignore-times \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_NORMAL
    run_command(command, path_studio)


def start_paid(message):
    path_studio = os.path.join(PATH_PAID, message['ip'])
    print(termcolor.colored('start_paid ...' + get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --size-only \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_PAID
    run_command(command, path_studio)


def start_paid_force(message):
    path_studio = os.path.join(PATH_PAID_FORCE, message['ip'])
    print(termcolor.colored('start_paid_force ...' + get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --ignore-times \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_PAID
    run_command(command, path_studio)


def run_command(command, path_studio):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        status = process.wait()
    except:
        time.sleep(5)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        status = process.wait()
        print(termcolor.colored('second try', 'red', attrs=['reverse']), flush=True)
    if status == 0:
        try:
            time.sleep(1)
            shutil.rmtree(path_studio)
            os.mkdir(path_studio)
            os.mkdir(os.path.join(path_studio, 'thumbnails'))
        except:
            print(termcolor.colored('File removal failed', 'red', attrs=['reverse']), flush=True)
    else:
        print(termcolor.colored('Non-zero status code: ' + str(status), 'red', attrs=['reverse']), flush=True)


def digest(ch, method, properties, body):
    start = time.time()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = json.loads(body)
    print(termcolor.colored(str(message), 'cyan'), flush=True)
    if message['tag'] == 'normal':
        start_normal(message)
    elif message['tag'] == 'normal_force':
        start_normal_force(message)
    elif message['tag'] == 'paid':
        start_paid(message)
    elif message['tag'] == 'paid_force':
        start_paid_force(message)
    else:
        print(termcolor.colored('Unknown tag context ↑↑↑', 'red', attrs=['reverse']), flush=True)
    end = time.time()
    print(
        termcolor.colored('Done in ' + str(time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))) + ' seconds ',
                          'green', attrs=['reverse']), flush=True)


def listen():
    host = '192.168.4.2'
    queue_name = 'studio-upload'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=0))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=digest, auto_ack=False)
    print(termcolor.colored('studio-upload started listening! ', 'green'), flush=True)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


def get_size(start_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except:
        print(termcolor.colored('error calculating size', 'red', attrs=['reverse']), flush=True)

    if total_size < 1024:
        size = str(round(total_size)) + ' Byte'
    elif total_size < 1024 ^ 2:
        size = str(round(total_size / 1024, 1)) + ' KB'
    elif total_size < 1024 * 1024 * 1024:
        size = str(round(total_size / (1024 * 1024), 1)) + ' MB'
    else:
        size = str(round(total_size / (1024 * 1024 * 1024), 1)) + ' GB'
    return size


if __name__ == '__main__':
    PATH_RSYNC = '/usr/local/bin/rsync'
    PATH_UPLOAD = '/home/film/upload'
    PATH_NORMAL = '/home/film/upload/normal'
    PATH_NORMAL_FORCE = '/home/film/upload/normal_force'
    PATH_PAID = '/home/film/upload/paid'
    PATH_PAID_FORCE = '/home/film/upload/paid_force'

    SFTP = 'sftp@cdn.alaatv.com:'
    PASSWORD = os.getenv("PASSWORD_SFTP")
    load_dotenv()
    PATH_UPSTREAM_NORMAL = '/alaa_media/cdn/media'
    PATH_UPSTREAM_PAID = '/alaa_media/cdn/paid/private'

    listen()
