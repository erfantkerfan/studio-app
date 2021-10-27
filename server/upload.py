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
NUMBER_OF_RETRIES = 3


def start_upload(message, src_path, dst_path):
    path_studio = os.path.join(src_path, message['ip'])
    print(termcolor.colored('start ' + message['tag'] + ' ... ' + helper.get_size(path_studio), 'yellow'), flush=True)

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

    command = MC_MIRROR + path_studio + os.path.sep + ' ' + dst_path
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def run_command(command):
    status = None
    retries = 0
    while status not in [0] or retries <= NUMBER_OF_RETRIES:
        try:
            print(termcolor.colored('started uploading process', 'yellow'), flush=True)
            retries += 1
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
            # wait in seconds for upload
            status = process.wait(timeout=20 * 60)
        except:
            print(termcolor.colored('retry number ' + str(retries) + ' failed', 'red', attrs=['reverse']), flush=True)
    return status


def cleanup(status, path_studio, user_id, type):
    if status == 0:
        update_duration(path_studio, user_id)
        try:
            time.sleep(1)
            if type in ['normal']:
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
        print(termcolor.colored('Non-zero status code: ' + str(status), 'red', attrs=['reverse']), flush=True)


# start processing message and route to needed function
# plus timing the call for better logging
def digest(ch, method, properties, body):
    start = time.time()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = json.loads(body)
    print(termcolor.colored(str(message), 'cyan'), flush=True)
    if message['tag'] == 'normal':
        start_upload(message, PATH_NORMAL, PATH_UPSTREAM_NORMAL)
    elif message['tag'] == 'paid':
        start_upload(message, PATH_PAID, PATH_UPSTREAM_PAID)
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
    PATH_UPLOAD = '/home/alaa/film/upload'
    PATH_NORMAL = PATH_UPLOAD + '/normal'
    PATH_PAID = PATH_UPLOAD + '/paid'
    PATH_UPSTREAM_NORMAL = 'myminio/media/'
    PATH_UPSTREAM_PAID = 'myminio/paid/'
    MC_MIRROR = 'mc mirror --quiet --preserve --region iran-tehran-homa '

    HEADERS = {
        'Accept': 'application/json',
        'Cookie': 'nocache=1',
        'Accept-Encoding': 'utf-8'
    }
    URL = "https://alaatv.com/api/v2/c/updateDuration"

    listen()
