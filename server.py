import json
import os
import shutil
import subprocess
import time

import pika
import termcolor


def start_studio(message):
    print(termcolor.colored('start_studio ...', 'yellow'), flush=True)
    status = 0
    path_studio = os.path.join(PATH_CONVERT, message['ip'])
    for folder in [item.name for item in os.scandir(path_studio) if item.is_dir()]:
        if os.path.isdir(os.path.join(path_studio, folder, PATH_HIGH)):
            if not os.path.exists(os.path.join(path_studio, folder, PATH_MID)):
                os.makedirs(os.path.join(path_studio, folder, PATH_MID))
            if not os.path.exists(os.path.join(path_studio, folder, PATH_LOW)):
                os.makedirs(os.path.join(path_studio, folder, PATH_LOW))
            for file in [item.name for item in os.scandir(os.path.join(path_studio, folder, PATH_HIGH)) if
                         item.is_file()]:
                try:
                    if file.endswith(('.mp4', '.MP4')):
                        in_high = os.path.join(path_studio, folder, PATH_HIGH, file)
                        out_mid = os.path.join(path_studio, folder, PATH_MID, file)
                        out_low = os.path.join(path_studio, folder, PATH_LOW, file)
                        command = PATH_FFMPEG + ' -y -i \"' + in_high + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 96k -movflags +faststart \"' + out_mid + '\" -threads 15 -sws_flags lanczos -s 426x240 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart \"' + out_low + '\" -threads 7'
                        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                                                   shell=True)
                        status = process.wait() + status
                except:
                    print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)
            if os.path.exists(os.path.join(path_studio, 'done', folder)):
                shutil.rmtree(os.path.join(path_studio, 'done', folder))
            shutil.move(os.path.join(path_studio, folder), os.path.join(path_studio, 'done', folder))


def start_announce(message):
    print(termcolor.colored('start_announce ...', 'yellow'), flush=True)
    status = 0
    for folder in [item.name for item in os.scandir(PATH_ANNOUNCE) if item.is_dir()]:
        if os.path.isdir(os.path.join(PATH_ANNOUNCE, folder, PATH_HIGH)):
            if not os.path.exists(os.path.join(PATH_ANNOUNCE, folder, PATH_MID)):
                os.makedirs(os.path.join(PATH_ANNOUNCE, folder, PATH_MID))
            if not os.path.exists(os.path.join(PATH_ANNOUNCE, folder, PATH_LOW)):
                os.makedirs(os.path.join(PATH_ANNOUNCE, folder, PATH_LOW))
            for file in [item.name for item in os.scandir(os.path.join(PATH_ANNOUNCE, folder, PATH_HIGH)) if
                         item.is_file()]:
                try:
                    if file.endswith(('.mp4', '.MP4')):
                        in_high = os.path.join(PATH_ANNOUNCE, folder, PATH_HIGH, file)
                        out_mid = os.path.join(PATH_ANNOUNCE, folder, PATH_MID, file)
                        out_low = os.path.join(PATH_ANNOUNCE, folder, PATH_LOW, file)
                        command = PATH_FFMPEG + ' -y -i \"' + in_high + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 854x854 -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart \"' + out_mid + '\" -threads 15 -sws_flags lanczos -s 426x426 -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 50k -movflags +faststart \"' + out_low + '\"  -threads 7'
                        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                                                   shell=True)
                        status = process.wait() + status
                except:
                    print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)
            if os.path.exists(os.path.join(PATH_ANNOUNCE, 'done', folder)):
                shutil.rmtree(os.path.join(PATH_ANNOUNCE, 'done', folder))
            shutil.move(os.path.join(PATH_ANNOUNCE, folder), os.path.join(PATH_ANNOUNCE, 'done', folder))


def start_axis(message):
    print(termcolor.colored('start_axis ...', 'yellow'), flush=True)
    status = 0
    path_studio = os.path.join(PATH_AXIS, message['ip'])
    for file in [item.name for item in os.scandir(path_studio) if item.is_file()]:
        try:
            if file.endswith(('.mkv', '.MKV')):
                try:
                    mp4 = file.replace('mkv', 'mp4')
                except:
                    mp4 = file.replace('MKV', 'mp4')
                in_mkv = os.path.join(path_studio, file)
                out_mp4 = os.path.join(path_studio, mp4)
                command = PATH_FFMPEG + ' -y -i \"' + in_mkv + '\" -metadata title="@alaa_sanatisharif" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"' + out_mp4 + '\" -threads 23'
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                status = process.wait() + status

                os.remove(in_mkv)
                if not os.path.exists(os.path.join(PATH_AXIS, 'done')):
                    os.makedirs(os.path.join(PATH_AXIS, 'done'))
                if os.path.exists(os.path.join(PATH_AXIS, 'done', mp4)):
                    os.remove(os.path.join(PATH_AXIS, 'done', mp4))
                shutil.move(out_mp4, os.path.join(PATH_AXIS, 'done'))
        except:
            print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)


def start_rabiea(message):
    print(termcolor.colored('start_rabiea ...', 'yellow'), flush=True)
    status = 0
    for file in [item.name for item in os.scandir(PATH_RABIEA) if item.is_file()]:
        try:
            if file.endswith(('.mp4', '.MP4')):
                if not os.path.exists(os.path.join(PATH_RABIEA, 'done')):
                    os.makedirs(os.path.join(PATH_RABIEA, 'done'))
                in_mp4 = os.path.join(PATH_RABIEA, file)
                out_mp4 = os.path.join(PATH_RABIEA, 'done', file)

                if message['tag'] == 'rabiea':
                    command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 1280x720 -profile:v baseline -level 3.0 -vcodec libx264 -crf 19 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 128k -movflags +faststart \"' + out_mp4 + '\" -threads 23'
                elif message['tag'] == 'rabiea-480':
                    command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 128k -movflags +faststart \"' + out_mp4 + '\" -threads 23'
                elif message['tag'] == 'rabiea-sizeless':
                    command = PATH_FFMPEG + ' -y -i \"' + in_mp4 + '\" -metadata title="@alaa_sanatisharif" -sws_flags lanczos -profile:v baseline -level 3.0 -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 96k -movflags +faststart \"' + out_mp4 + '\" -threads 23'

                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                status = process.wait() + status
                if os.path.exists(os.path.join(PATH_RABIEA, file)):
                    os.remove(os.path.join(PATH_RABIEA, file))
        except:
            print(termcolor.colored('failed', 'red', attrs=['reverse']), flush=True)


def digest(ch, method, properties, body):
    start = time.time()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = json.loads(body)
    print(termcolor.colored(message, 'cyan'), flush=True)
    if message['tag'] == 'studio':
        start_studio(message)
    elif message['tag'] == 'announce':
        start_announce(message)
    elif message['tag'] == 'axis':
        start_axis(message)
    elif message['tag'] in ['rabiea', 'rabiea-480', 'rabiea-sizeless']:
        start_rabiea(message)
    else:
        print('Unknown tag context ... ->' + str(message), flush=True)
    end = time.time()
    print(
        termcolor.colored('Done in ' + str(time.strftime('%H:%M:%S', time.gmtime(round(end - start, 1)))) + ' seconds ',
                          'green', attrs=['reverse']), flush=True)


def listen():
    host = '192.168.4.2'
    queue_name = 'studio-app'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=0))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=digest, auto_ack=False)
    print(termcolor.colored('studio-app started listening!', 'green'), flush=True)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    PATH_FFMPEG = '/home/alaa/bin/ffmpeg'
    PATH_ANNOUNCE = '/home/film/announce'
    PATH_CONVERT = '/home/film/convert'
    PATH_AXIS = '/home/film/axis'
    PATH_RABIEA = '/home/film/rabiea'

    PATH_HIGH = 'HD_720p'
    PATH_MID = 'hq'
    PATH_LOW = '240p'

    listen()
