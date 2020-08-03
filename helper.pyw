import time
import datetime
import os
import logging


def parse_seconds(t):
    if t in ['', ' ', None]:
        return 0
    tx = time.strptime(t, '%H:%M:%S')
    seconds = datetime.timedelta(hours=tx.tm_hour, minutes=tx.tm_min, seconds=tx.tm_sec).total_seconds()
    return seconds


def setup_logging():
    if not os.path.exists('log.txt'):
        with open('log.txt', 'w+') as _:
            pass

    with open('log.txt', 'r+') as logfile:
        content = logfile.readlines()
        content = content[-1000:]
        logfile.seek(0)
        logfile.writelines(content)
        logfile.truncate()

    logging.basicConfig(filename='log.txt',
                        filemode='a',
                        format='%(asctime)s ---> %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.CRITICAL)
