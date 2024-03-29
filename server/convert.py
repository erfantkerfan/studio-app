import json
import os
import shutil
import subprocess
import threading
import time
from threading import Thread

import pika
import termcolor

import helper

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
    print(termcolor.colored('start_convert ... ' + helper.get_size(path_studio), 'yellow'), flush=True)
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


def start_tablet(message):
    status = 0
    # get client folder
    path_studio = os.path.join(PATH_TABLET, message['ip'])
    print(termcolor.colored('start_tablet ... ' + helper.get_size(path_studio), 'yellow'), flush=True)
    for file in [item.name for item in os.scandir(path_studio) if item.is_file()]:
        try:
            if file.endswith(('.mp4', '.MP4')):
                # generate mp4 name
                mp4 = file.replace('mp4', 'out.mp4').replace('MP4', 'OUT.MP4')
                in_mp4 = os.path.join(path_studio, file)
                # generate mp4 absolute path
                out_mp4 = os.path.join(path_studio, mp4)
                command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 960x720 -profile:v baseline -level 3.0 -vcodec libx264 -crf 18 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 320k -movflags +faststart \"' + out_mp4 + '\"'
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                status = process.wait() + status
                # remove mkv after convert
                os.remove(in_mp4)
                if not os.path.exists(os.path.join(path_studio, 'done')):
                    os.makedirs(os.path.join(path_studio, 'done'))
                if os.path.exists(os.path.join(path_studio, 'done', mp4)):
                    os.remove(os.path.join(path_studio, 'done', mp4))
                shutil.move(out_mp4, os.path.join(path_studio, 'done'))
        except:
            print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)


def start_announce(message):
    print(termcolor.colored('start_announce ... ' + helper.get_size(PATH_ANNOUNCE), 'yellow'), flush=True)
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
    print(termcolor.colored('start_rabiea ... ' + helper.get_size(PATH_RABIEA), 'yellow'), flush=True)
    status = 0
    for file in [item.name for item in os.scandir(PATH_RABIEA) if item.is_file()]:
        try:
            if file.endswith(('.mp4', '.MP4')):
                if not os.path.exists(os.path.join(PATH_RABIEA, 'done')):
                    os.makedirs(os.path.join(PATH_RABIEA, 'done'))
                # generate input and output filename
                in_mp4 = os.path.join(PATH_RABIEA, file)
                out_mp4 = os.path.join(PATH_RABIEA, 'done', 'HQ-' + file)
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


# start processing message and route to needed function
# plus timing the call for better logging
def digest(ch, method, properties, body):
    start = time.perf_counter()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = json.loads(body)
    print(termcolor.colored(message, 'cyan'), flush=True)
    if message['tag'] == 'convert':
        start_convert(message)
    elif message['tag'] == 'tablet':
        start_tablet(message)
    elif message['tag'] == 'announce':
        start_announce(message)
    elif message['tag'] in ['rabiea', 'rabiea-480', 'rabiea-sizeless']:
        start_rabiea(message)
    else:
        print('Unknown tag context ... ->' + str(message), flush=True)
    end = time.perf_counter()
    helper.send_message(message['ip'], message['tag'] + ' Done in ' + str(
        time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))))
    print(
        termcolor.colored('Done in ' + str(time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))),
                          'green', attrs=['reverse']), flush=True)


# start listening to rabbit-mq server
def listen():
    host = '192.168.4.3'
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
    PATH_FFMPEG = '/usr/bin/ffmpeg'
    PATH_ANNOUNCE = '/home/alaa/film/announce'
    PATH_CONVERT = '/home/alaa/film/convert'
    PATH_TABLET = '/home/alaa/film/tablet'
    PATH_RABIEA = '/home/alaa/film/rabiea'

    PATH_HIGH = 'HD_720p'
    PATH_MID = 'hq'
    PATH_LOW = '240p'

    listen()
