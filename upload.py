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

SIMULTANEOUS_THREADS = 20


def start_normal(message):
    path_studio = os.path.join(PATH_NORMAL, message['ip'])
    print(termcolor.colored('start_normal ... ' + get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --size-only \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_NORMAL
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def start_normal_force(message):
    path_studio = os.path.join(PATH_NORMAL_FORCE, message['ip'])
    print(termcolor.colored('start_normal_force ... ' + get_size(path_studio), 'yellow'), flush=True)

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
            threads.append(Thread(name='t: ' + str(fp), target=webp, args=(fp,)))
            threads[-1].start()
    # stay here until all threads are finished
    while any([t.is_alive for t in threads]):
        threads = [t for t in threads if t.is_alive()]

    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --ignore-times \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_NORMAL
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def start_paid(message):
    path_studio = os.path.join(PATH_PAID, message['ip'])
    print(termcolor.colored('start_paid ... ' + get_size(path_studio), 'yellow'), flush=True)
    command = 'sshpass -p \"' + PASSWORD + '\" rsync -avhWP --no-compress --size-only \"' + path_studio + os.path.sep + '\" ' + SFTP + PATH_UPSTREAM_PAID
    status = run_command(command)
    cleanup(status, path_studio, message['user_id'], message['tag'])


def start_paid_force(message):
    path_studio = os.path.join(PATH_PAID_FORCE, message['ip'])
    print(termcolor.colored('start_paid_force ... ' + get_size(path_studio), 'yellow'), flush=True)

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
            threads.append(Thread(name='t: ' + str(fp), target=webp, args=(fp,)))
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
            status = process.wait()
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
        print(termcolor.colored('Non-zero status code: ' + str(status) + get_rsync_error(status), 'red',
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


def webp(path):
    command = 'cwebp -quiet -mt -m 6 -q 80 -sharp_yuv -alpha_filter best -pass 10 -segments 4 -af \"' + path + '\" -o \"' + path + '.webp' + '\"'
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        process.wait()
    except:
        pass


# get size for better logging (except 'done' folder)
def get_size(start_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp) and 'done' not in dirpath:
                    total_size += os.path.getsize(fp)
        if total_size < 1024:
            size = str(round(total_size)) + ' Byte'
        elif total_size < 1024 ^ 2:
            size = str(round(total_size / 1024, 1)) + ' KB'
        elif total_size < 1024 * 1024 * 1024:
            size = str(round(total_size / (1024 * 1024), 1)) + ' MB'
        else:
            size = str(round(total_size / (1024 * 1024 * 1024), 1)) + ' GB'
        return size
    except:
        return 'error calculating size'


def get_rsync_error(code):
    errors = {
        0: ' -> Success',
        1: ' -> Syntax or usage error',
        2: ' -> Protocol incompatibility',
        3: ' -> Errors selecting input/output files, dirs',
        4: ' -> Requested action not supported: an attempt was made to manipulate 64-bit files on a platform that cannot support them; or an option was specified; that is supported by the client and not by the server.',
        5: ' -> Error starting client-server protocol',
        6: ' -> Daemon unable to append to log-file',
        10: ' -> Error in socket I/O',
        11: ' -> Error in file I/O',
        12: ' -> Error in rsync protocol data stream',
        13: ' -> Errors with program diagnostics',
        14: ' -> Error in IPC code',
        20: ' -> Received SIGUSR1 or SIGINT',
        21: ' -> Some error returned by waitpid()',
        22: ' -> Error allocating core memory buffers',
        23: ' -> Partial transfer due to error',
        24: ' -> Partial transfer due to vanished source files',
        25: ' -> The --max-delete limit stopped deletions',
        30: ' -> Timeout in data send/receive',
        35: ' -> Timeout waiting for daemon connection',
        255: ' -> server did not accept handshake',
    }
    return errors.get(code, '')


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
    PATH_RSYNC = '/usr/local/bin/rsync'
    PATH_UPLOAD = '/home/film/upload'
    PATH_NORMAL = '/home/film/upload/normal'
    PATH_NORMAL_FORCE = '/home/film/upload/normal_force'
    PATH_PAID = '/home/film/upload/paid'
    PATH_PAID_FORCE = '/home/film/upload/paid_force'

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
