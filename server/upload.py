import base64
import json
import os
import shutil
import subprocess
import threading
import time
from threading import Thread

import pika
import requests
import termcolor
from dotenv import load_dotenv

import helper

SIMULTANEOUS_THREADS = 20


def start_normal(message):
    path_studio = os.path.join(PATH_NORMAL, message['ip'])
    print(termcolor.colored('start_normal ... ' + helper.get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --size-only \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_NORMAL
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def start_normal_force(message):
    path_studio = os.path.join(PATH_NORMAL_FORCE, message['ip'])
    print(termcolor.colored('start_normal_force ... ' + helper.get_size(path_studio), 'yellow'), flush=True)

    print(termcolor.colored('start_webp_generation', 'green'), flush=True)
    threads = []
    for dirpath, dirnames, filenames in os.walk(path_studio):
        for file in filenames:
            fp = os.path.join(dirpath, file)
            if os.path.islink(fp) or not fp.lower().endswith(('.jpg', '.jpeg', 'png')):
                continue
            while threading.activeCount() > SIMULTANEOUS_THREADS:
                pass
            threads = [t for t in threads if t.is_alive()]
            threads.append(Thread(name='t: ' + str(fp), target=helper.webp, args=(fp,)))
            threads[-1].start()
    # stay here until all threads are finished
    while any([t.is_alive for t in threads]):
        threads = [t for t in threads if t.is_alive()]

    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --ignore-times \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_NORMAL
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def start_paid(message):
    path_studio = os.path.join(PATH_PAID, message['ip'])
    print(termcolor.colored('start_paid ... ' + helper.get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --size-only \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_PAID
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def start_paid_force(message):
    path_studio = os.path.join(PATH_PAID_FORCE, message['ip'])
    print(termcolor.colored('start_paid_force ... ' + helper.get_size(path_studio), 'yellow'), flush=True)

    threads = []
    for dirpath, dirnames, filenames in os.walk(path_studio):
        for file in filenames:
            fp = os.path.join(dirpath, file)
            if os.path.islink(fp) or not fp.lower().endswith(('.jpg', '.jpeg', 'png')):
                continue
            while threading.activeCount() > SIMULTANEOUS_THREADS:
                pass
            print(termcolor.colored('start_webp_generation', 'green'), flush=True)
            threads = [t for t in threads if t.is_alive()]
            threads.append(Thread(name='t: ' + str(fp), target=helper.webp, args=(fp,)))
            threads[-1].start()
    # stay here until all threads are finished
    while any([t.is_alive for t in threads]):
        threads = [t for t in threads if t.is_alive()]

    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --ignore-times \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_PAID
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def run_command(command):
    status = None
    while status in [None, 255]:
        try:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
            # wait in seconds for upload
            status = process.wait(timeout=20 * 60)
        except:
            print(termcolor.colored('second try', 'red', attrs=['reverse']), flush=True)
    return status


def cleanup(status, path_studio, user_id, type):
    if status == 0:
        update_duration(path_studio, user_id)
        try:
            time.sleep(1)
            if type in ['normal', 'normal_force']:
                shutil.rmtree(path_studio)
                os.mkdir(path_studio)
                os.mkdir(os.path.join(path_studio, 'thumbnails'))
            else:
                for path, subdirs, files in os.walk(path_studio):
                    for name in files:
                        try:
                            os.remove(os.path.join(path, name))
                        except:
                            pass
        except:
            print(termcolor.colored('File removal failed', 'red', attrs=['reverse']), flush=True)
    else:
        print(termcolor.colored('Non-zero status code: ' + str(status) + helper.get_rsync_error(status), 'red',
                                attrs=['reverse']), flush=True)


# start processing message and route to needed function
# plus timing the call for better logging
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
    helper.send_message(message['ip'], message['tag'] + ' Done in ' + str(
        time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))))
    print(
        termcolor.colored('Done in ' + str(time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))),
                          'green', attrs=['reverse']), flush=True)


# update file/phamphlet duration via api call
def update_duration(path_studio, user_id):
    duration = {
        'content': [],
        'user_id': user_id
    }
    for dirpath, dirnames, filenames in os.walk(path_studio):
        for file in [a for a in filenames if a.lower().endswith('.mp4')]:
            duration['content'].append({"file_name": file, "set_id": os.path.basename(os.path.dirname(dirpath))})
    duration['content'] = str(duration['content']).replace('"', '').replace("'", '"')
    status_code = None
    tries = 0
    while status_code != 200:
        try:
            response = requests.request("PUT", URL, headers=HEADERS, data=duration)
            status_code = response.status_code
            print(termcolor.colored('Duration updated with status ' + str(status_code), 'green',
                                    attrs=['reverse']), flush=True)
        except:
            print(termcolor.colored('Duration not updated', 'red', attrs=['reverse']), flush=True)
        tries += 1
        if tries == 10:
            print(termcolor.colored('Duration not updated in 10 tries', 'red', attrs=['reverse']), flush=True)
            break
        time.sleep(3)


# start listening to rabbit-mq server
def listen():
    host = '192.168.4.3'
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


if __name__ == '__main__':
    load_dotenv()
    PATH_RSYNC = '/usr/bin/rsync'
    PATH_UPLOAD = '/home/alaa/film/upload'
    PATH_NORMAL = '/home/alaa/film/upload/normal'
    PATH_NORMAL_FORCE = '/home/alaa/film/upload/normal_force'
    PATH_PAID = '/home/alaa/film/upload/paid'
    PATH_PAID_FORCE = '/home/alaa/film/upload/paid_force'

    SFTP = 'sftp@cdn.alaatv.com:'
    PASSWORD = base64.b64decode(os.getenv("PASSWORD_SFTP").encode('ascii')).decode('ascii')
    # GENERATED_PASSWORD = base64.b64encode('XXX'.encode('ascii')).decode('ascii')
    load_dotenv()
    PATH_UPSTREAM_NORMAL = '/alaa_media/cdn/media'
    PATH_UPSTREAM_PAID = '/alaa_media/cdn/paid/private'

    HEADERS = {
        'Accept': 'application/json',
        'Cookie': 'nocache=1',
        'Accept-Encoding': 'utf-8'
    }
    URL = "https://alaatv.com/api/v2/c/updateDuration"

    listen()
