import datetime
import json
import os

import subprocess

import pika


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


def webp(path):
    command = 'cwebp -quiet -mt -m 6 -q 80 -sharp_yuv -alpha_filter best -pass 10 -segments 4 -af \"' + path + '\" -o \"' + path + '.webp' + '\"'
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        process.wait()
        pass
    except:
        pass


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
