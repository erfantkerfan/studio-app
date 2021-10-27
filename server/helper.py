import datetime
import json
import os
import subprocess

import pika

UPLOAD_SIZE_WARNING_GIGS = 10


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
        elif total_size < 1024 ** 2:
            size = str(round(total_size / 1024, 1)) + ' KB'
        elif total_size < 1024 ** 3:
            size = str(round(total_size / (1024 ** 2), 1)) + ' MB'
        else:
            size_in_gig = round(total_size / (1024 ** 3), 1)
            size = str(size_in_gig) + ' GB'
            if size_in_gig >= UPLOAD_SIZE_WARNING_GIGS:
                size += ' FILE TOO LARGE ╭∩╮ (ò╭╮Ó ) '

        return size
    except:
        return 'error calculating size'


def webp(path):
    command = 'cwebp -quiet -mt -m 6 -q 80 -sharp_yuv -alpha_filter best -pass 10 -segments 4 -af \"' + path + '\" -o \"' + path + '.webp' + '\"'
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        process.wait()
        pass
    except:
        pass


def send_message(to, text):
    host = '192.168.4.3'
    message = {
        'tag': 'text',
        'text': text,
        'sender': 'server',
        'ip': host,
        'user_id': 0,
        'datetime': str(datetime.datetime.now())
    }
    queue_name = to
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=json.dumps(message))
    connection.close()
