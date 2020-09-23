import json
import os
import shutil
import subprocess
import threading
import time
from threading import Thread

import pika
import termcolor

# number of files handled by ffmepg in convert method
SIMULTANEOUS_THREADS = 5


def single_convert(command):
    global status
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
    temp = process.wait()
    status = temp + status
    return None


def start_convert(message):
    global status
    status = 0
    threads = []
    # get client folder
    path_studio = os.path.join(PATH_CONVERT, message['ip'])
    print(termcolor.colored('start_convert ... ' + get_size(path_studio), 'yellow'), flush=True)
    for set in [item.name for item in os.scandir(path_studio) if item.is_dir()]:
        if os.path.isdir(os.path.join(path_studio, set, PATH_HIGH)):
            # create output folders
            if not os.path.exists(os.path.join(path_studio, set, PATH_MID)):
                os.makedirs(os.path.join(path_studio, set, PATH_MID))
            if not os.path.exists(os.path.join(path_studio, set, PATH_LOW)):
                os.makedirs(os.path.join(path_studio, set, PATH_LOW))
            for file in [item.name for item in os.scandir(os.path.join(path_studio, set, PATH_HIGH)) if item.is_file()]:
                try:
                    if file.endswith(('.mp4', '.MP4')):
                        # generate output file names
                        in_high = os.path.join(path_studio, set, PATH_HIGH, file)
                        out_mid = os.path.join(path_studio, set, PATH_MID, file)
                        out_low = os.path.join(path_studio, set, PATH_LOW, file)
                        command = PATH_FFMPEG + ' -y -i \"' + in_high + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 96k -movflags +faststart \"' + out_mid + '\" -sws_flags lanczos -s 426x240 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart \"' + out_low + '\"'
                        # wait for available threads
                        while threading.activeCount() > SIMULTANEOUS_THREADS:
                            pass
                            time.sleep(1)
                        # remove finished stacks
                        threads = [t for t in threads if t.is_alive()]
                        # push thread to stack
                        threads.append(Thread(name='t: ' + str(in_high), target=single_convert, args=(command,)))
                        threads[-1].start()

                except:
                    print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)

            # wait for all threads to finish
            while any([t.is_alive for t in threads]):
                threads = [t for t in threads if t.is_alive()]

            nondestructive_move(os.path.join(path_studio, set), os.path.join(path_studio, 'done'), set)


def start_announce(message):
    print(termcolor.colored('start_announce ... ' + get_size(PATH_ANNOUNCE), 'yellow'), flush=True)
    status = 0
    for set in [item.name for item in os.scandir(PATH_ANNOUNCE) if item.is_dir()]:
        if os.path.isdir(os.path.join(PATH_ANNOUNCE, set, PATH_HIGH)):
            if not os.path.exists(os.path.join(PATH_ANNOUNCE, set, PATH_MID)):
                os.makedirs(os.path.join(PATH_ANNOUNCE, set, PATH_MID))
            if not os.path.exists(os.path.join(PATH_ANNOUNCE, set, PATH_LOW)):
                os.makedirs(os.path.join(PATH_ANNOUNCE, set, PATH_LOW))
            for file in [item.name for item in os.scandir(os.path.join(PATH_ANNOUNCE, set, PATH_HIGH)) if
                         item.is_file()]:
                try:
                    if file.endswith(('.mp4', '.MP4')):
                        in_high = os.path.join(PATH_ANNOUNCE, set, PATH_HIGH, file)
                        out_mid = os.path.join(PATH_ANNOUNCE, set, PATH_MID, file)
                        out_low = os.path.join(PATH_ANNOUNCE, set, PATH_LOW, file)
                        command = PATH_FFMPEG + ' -y -i \"' + in_high + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 854x854 -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart \"' + out_mid + '\" -sws_flags lanczos -s 426x426 -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 50k -movflags +faststart \"' + out_low + '\"'
                        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                                                   shell=True)
                        status = process.wait() + status
                except:
                    print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)

            nondestructive_move(os.path.join(PATH_ANNOUNCE, set), os.path.join(PATH_ANNOUNCE, 'done'), set)


def start_rabiea(message):
    print(termcolor.colored('start_rabiea ... ' + get_size(PATH_RABIEA), 'yellow'), flush=True)
    status = 0
    for file in [item.name for item in os.scandir(PATH_RABIEA) if item.is_file()]:
        try:
            if file.endswith(('.mp4', '.MP4')):
                if not os.path.exists(os.path.join(PATH_RABIEA, 'done')):
                    os.makedirs(os.path.join(PATH_RABIEA, 'done'))
                # generate input and output filename
                in_mp4 = os.path.join(PATH_RABIEA, file)
                out_mp4 = os.path.join(PATH_RABIEA, 'done', file)
                # generate different command types
                if message['tag'] == 'rabiea':
                    command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 1280x720 -profile:v baseline -level 3.0 -vcodec libx264 -crf 19 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 128k -movflags +faststart \"' + out_mp4 + '\"'
                elif message['tag'] == 'rabiea-480':
                    command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 128k -movflags +faststart \"' + out_mp4 + '\"'
                elif message['tag'] == 'rabiea-sizeless':
                    command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 96k -movflags +faststart \"' + out_mp4 + '\"'

                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                status = process.wait() + status
                if os.path.exists(os.path.join(PATH_RABIEA, file)):
                    os.remove(os.path.join(PATH_RABIEA, file))
        except:
            print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)


# move folder safe (add 'new' if exists)
def nondestructive_move(source, destination, set):
    if not os.path.exists(os.path.join(destination, set)):
        shutil.move(source, os.path.join(destination, set))
    else:
        nondestructive_move(source, destination, set + ' new')


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
    if message['tag'] == 'convert':
        start_convert(message)
    elif message['tag'] == 'announce':
        start_announce(message)
    elif message['tag'] in ['rabiea', 'rabiea-480', 'rabiea-sizeless']:
        start_rabiea(message)
    else:
        print('Unknown tag context ... ->' + str(message), flush=True)
    end = time.time()
    print(
        termcolor.colored('Done in ' + str(time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))),
                          'green', attrs=['reverse']), flush=True)


# start listening to rabbit-mq server
def listen():
    host = '192.168.4.2'
    queue_name = 'studio-convert'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=0))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=digest, auto_ack=False)
    print(termcolor.colored('studio-convert started listening!', 'green'), flush=True)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    PATH_FFMPEG = '/home/alaa/bin/ffmpeg'
    PATH_ANNOUNCE = '/home/film/announce'
    PATH_CONVERT = '/home/film/convert'
    PATH_RABIEA = '/home/film/rabiea'

    PATH_HIGH = 'HD_720p'
    PATH_MID = 'hq'
    PATH_LOW = '240p'

    listen()
