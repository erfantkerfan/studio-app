import json
import os
import shutil
import subprocess
import time

import pika
import termcolor


def start_axis(message):
    status = 0
    # get client folder
    path_studio = os.path.join(PATH_AXIS, message['ip'])
    print(termcolor.colored('start_axis ... ' + get_size(path_studio), 'yellow'), flush=True)
    for file in [item.name for item in os.scandir(path_studio) if item.is_file()]:
        try:
            if file.endswith(('.mkv', '.MKV')):
                # generate mp4 name
                mp4 = file.replace('mkv', 'mp4').replace('MKV', 'mp4')
                in_mkv = os.path.join(path_studio, file)
                # generate mp4 absolute path
                out_mp4 = os.path.join(path_studio, mp4)
                command = PATH_FFMPEG + ' -y -i \"' + in_mkv + '\" -metadata title="@alaa_sanatisharif" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"' + out_mp4 + '\" -threads 23'
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                status = process.wait() + status
                # remove mkv after convert
                os.remove(in_mkv)
                if not os.path.exists(os.path.join(PATH_AXIS, 'done')):
                    os.makedirs(os.path.join(PATH_AXIS, 'done'))
                if os.path.exists(os.path.join(PATH_AXIS, 'done', mp4)):
                    os.remove(os.path.join(PATH_AXIS, 'done', mp4))
                shutil.move(out_mp4, os.path.join(PATH_AXIS, 'done'))
        except:
            print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)


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


# start processing message and route to needed function
# plus timing the call for better logging
def digest(ch, method, properties, body):
    start = time.time()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = json.loads(body)
    print(termcolor.colored(message, 'cyan'), flush=True)
    if message['tag'] == 'axis':
        start_axis(message)
    else:
        print('Unknown tag context ... ->' + str(message), flush=True)
    end = time.time()
    print(
        termcolor.colored('Done in ' + str(time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))),
                          'green', attrs=['reverse']), flush=True)


# start listening to rabbit-mq server
def listen():
    host = '192.168.4.2'
    queue_name = 'studio-axis'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=0))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=digest, auto_ack=False)
    print(termcolor.colored('studio-axis started listening!', 'green'), flush=True)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    PATH_FFMPEG = '/home/alaa/bin/ffmpeg'
    PATH_AXIS = '/home/film/axis'

    listen()
