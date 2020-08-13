import hashlib
import logging
import subprocess
import time
import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk
from PIL import ImageTk, Image
import requests
import json
import os
import re
import threading
from win10toast import ToastNotifier
import pika
import socket
from functools import partial


# TODO: self update
# TODO: cover upload methods
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


def attempt_login():
    url = "https://alaatv.com/api/v2/login"
    status_code = None
    headers = {
        'Accept': 'application/json',
        'Cookie': 'nocache=1',
        'Accept-Encoding': 'utf-8'
    }
    while status_code != 200:
        credentials = Login()
        payload = {'mobile': credentials.mobile, 'password': credentials.password}
        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            status_code = response.status_code
            data = json.loads(response.content)
        except:
            status_code = None
        try:
            if str(data['data']['user']['first_name']) == "None":
                status_code = None
                user_id = None
            else:
                name = str(data['data']['user']['first_name']) + ' ' + str(data['data']['user']['last_name'])
                user_id = str(data['data']['user']['id'])
        except:
            name = "کاربر ناشناس"
            user_id = "Unknown"
        logging.critical("logged in user_id: " + user_id)
    return data['data']['user']


class Login(object):
    def __init__(self):
        self.root = tk.Tk()
        self.add_menu()
        self.init_window()
        self.load_landing()
        self.root.mainloop()

    def add_menu(self):
        self.menubar = tk.Menu(self.root)
        self.add_voice("Quit", self.quit_window)
        self.config_menu()

    def init_window(self):
        self.root.geometry("250x150")
        self.root.resizable(height=None, width=None)
        self.root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.root.title('Alaa studio app')

    def load_landing(self):
        self.mblbox = tk.Entry(self.root)
        self.pwdbox = tk.Entry(self.root, show='*')

        self.x1 = tk.Label(self.root, text='mobile')
        self.x1.pack(side='top')
        self.mblbox.pack(side='top')

        self.x2 = tk.Label(self.root, text='password')
        self.x2.pack(side='top')

        self.pwdbox.pack(side='top')
        self.pwdbox.bind('<Return>', self.onpwdentry)

        self.x3 = tk.Button(self.root, command=self.onpwdentry, text='Login')
        self.x3.pack(side='top', pady=10)

    def add_voice(self, label, command):
        self.menubar.add_command(label=label, command=command)

    def config_menu(self):
        self.root.config(menu=self.menubar)

    def onpwdentry(self, event):
        self.password = self.pwdbox.get()
        self.mobile = self.mblbox.get()
        self.root.destroy()

    def quit_window(self):
        self.root.destroy()
        os._exit(0)


class Main(object):
    """load the main window"""

    def __init__(self, user):
        self.user_id = user['id']
        self.root = tk.Tk()
        self.add_menu()
        self.init_window()
        self.load_landing()
        self.root.mainloop()

    def load_landing(self):
        self.config_menu()
        self.welcome_text = tk.Label(self.root, text=os.linesep * 3 + 'سلام ' + user['first_name'] + ' ' + user[
            'last_name'] + ' عزیز')
        self.welcome_text.pack()
        self.root.update()

    def init_window(self):
        self.root.geometry("400x300")
        self.root.resizable(height=None, width=None)
        self.root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.root.title('Alaa studio app')

    def add_menu(self):
        self.menubar = tk.Menu(self.root)
        self.add_voice("Axis", self.axis)
        self.rabi_menu = tk.Menu(self.menubar, tearoff=0)
        self.rabi_menu.add_command(label='studio', command=partial(self.send_convert_command, 'studio'))
        self.rabi_menu.add_command(label='announce', command=partial(self.send_convert_command, 'announce'))
        self.rabi_menu.add_command(label='rabiea', command=partial(self.send_convert_command, 'rabiea'))
        self.rabi_menu.add_command(label='rabiea-480', command=partial(self.send_convert_command, 'rabiea-480'))
        self.rabi_menu.add_command(label='rabiea-sizeless',
                                   command=partial(self.send_convert_command, 'rabiea-sizeless'))
        self.menubar.add_cascade(label='Convert', menu=self.rabi_menu)
        self.add_voice('Quit', self.quit_window)
        self.config_menu()

    def add_voice(self, label, command):
        self.menubar.add_command(label=label, command=command)

    def config_menu(self):
        self.root.config(menu=self.menubar)

    def quit_window(self):
        self.root.destroy()
        os._exit(0)

    """axis section"""

    def axis(self):
        self.file_name = filedialog.askopenfilename(filetypes=(('mkv files', '*.mkv'), ('All files', '*.*')))
        if self.file_name == '':
            return None
        directory = os.path.join(os.path.dirname(self.file_name), 'mp4')
        if not os.path.exists(directory):
            os.makedirs(directory)
        modified_file_name = os.path.join(directory, os.path.basename(self.file_name).replace('mkv', 'mp4'))
        thread = threading.Thread(target=self.start_axis, args=(self.file_name, modified_file_name))
        self.root.protocol('WM_DELETE_WINDOW', self.root.iconify)
        self.welcome_text.pack_forget()
        self.root.config(menu='')
        self.space = tk.Label(self.root, text=os.linesep * 3)
        self.space.pack()
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_bar.pack()
        self.root.update()

        self.ffmpeg_time = ''
        thread.start()
        while thread.is_alive():
            try:
                self.percent_text.pack_forget()
            except:
                pass
            try:
                percent = os.path.getsize(modified_file_name) / os.path.getsize(self.file_name) * 100
                self.progress_bar['value'] = percent
            except:
                pass
            self.percent_text = tk.Label(self.root, text='مدت زمان تبدیل شده' + os.linesep + self.ffmpeg_time)
            self.percent_text.pack()
            self.root.update()

        os.startfile(directory.replace('/', '\\'))
        self.root.protocol('WM_DELETE_WINDOW', self.quit_window)
        self.space.pack_forget()
        self.progress_bar.pack_forget()
        self.percent_text.pack_forget()
        self.config_menu()
        self.root.update()

        toaster = ToastNotifier()
        toaster.show_toast('Axis Finished',
                           self.file_name,
                           icon_path='alaa.ico',
                           duration=10,
                           threaded=True)
        self.root.destroy()
        self.__init__(user)

    def start_axis(self, input, output):
        command = "ffmpeg -y -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"" + output + "\""
        logging.critical('axis command: ' + command)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True, shell=True)
        for line in self.process.stdout:
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.ffmpeg_time = reg.group(0) if reg else ''
        return None

    """convert section"""

    def convert(self):
        self.file_name = filedialog.askopenfilename(filetypes=(('mp4 files', '*.mp4'), ('All files', '*.*')))
        regex = re.compile(r'C:\\Alaa\\Finish\\\d{3,4}\\HD_720p')
        if self.file_name == '':
            return None
        elif not regex.match(str(self.file_name).replace('/', '\\')):
            toaster = ToastNotifier()
            toaster.show_toast('Path Invalid',
                               r'select a file in C:\Alaa\Finish',
                               icon_path='alaa.ico',
                               duration=2,
                               threaded=True)
            return None

        directory_hq = os.path.join(os.path.dirname(os.path.dirname(self.file_name)), 'hq')
        if not os.path.exists(directory_hq):
            os.makedirs(directory_hq)
        directory_240p = os.path.join(os.path.dirname(os.path.dirname(self.file_name)), '240p')
        if not os.path.exists(directory_240p):
            os.makedirs(directory_240p)

        command = "ffprobe -v error -hide_banner -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -i \"" + str(
            self.file_name) + "\""
        logging.critical('ffprobe command: ' + command)
        ffprobe_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, shell=True)
        out, err = ffprobe_process.communicate()
        reg = re.search('\d*\.\d*', str(err) + str(out))
        self.total_duration = float(reg.group(0)) if reg else parse_seconds('00:15:00')
        modified_file_name_hq = os.path.join(directory_hq, os.path.basename(self.file_name))
        modified_file_name_240p = os.path.join(directory_240p, os.path.basename(self.file_name))
        self.root.protocol('WM_DELETE_WINDOW', self.root.iconify)
        thread = threading.Thread(target=self.start_convert,
                                  args=(self.file_name, modified_file_name_hq, modified_file_name_240p))
        self.welcome_text.pack_forget()
        self.root.config(menu='')
        self.space = tk.Label(self.root, text=os.linesep * 1)
        self.space.pack()
        self.title_hq = tk.Label(self.root, text='HQ')
        self.title_hq.pack()
        self.progress_hq = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_hq.pack()
        self.title_240p = tk.Label(self.root, text='240p')
        self.title_240p.pack()
        self.progress_240p = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_240p.pack()
        self.root.update()
        self.ffmpeg_time_hq = ''
        self.ffmpeg_time_240p = ''
        thread.start()
        while thread.is_alive():
            self.progress_hq['value'] = parse_seconds(self.ffmpeg_time_hq) / self.total_duration * 100
            self.progress_240p['value'] = parse_seconds(self.ffmpeg_time_240p) / self.total_duration * 100
            self.root.update()

        os.startfile(os.path.dirname(self.file_name).replace('/', '\\'))
        self.root.protocol('WM_DELETE_WINDOW', self.quit_window)
        self.space.pack_forget()
        self.title_hq.pack_forget()
        self.progress_hq.pack_forget()
        self.title_240p.pack_forget()
        self.progress_240p.pack_forget()
        self.config_menu()
        self.root.update()

        toaster = ToastNotifier()
        toaster.show_toast('Convert Finished',
                           self.file_name,
                           icon_path='alaa.ico',
                           duration=10,
                           threaded=True)
        self.root.destroy()
        self.__init__()

    def start_convert(self, input, output_hq, output_240p):
        # TODO:libfdk_aac
        # TODO:big file size
        # command_hq = "ffmpeg -y  -v quiet -stats -i \"" + str(
        #     input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec aac -ab 96k -movflags +faststart \"" + output_hq + "\""
        command_hq = "ffmpeg -y -hwaccel cuda -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos -s 854x480 -profile:v baseline -level 3.0 -vcodec h264_nvenc -crf 27 -r 24 -preset slow -pix_fmt yuv420p -tune film -acodec aac -ab 96k -movflags +faststart \"" + output_hq + "\""
        logging.critical('convert command: ' + command_hq)
        self.process_hq = subprocess.Popen(command_hq, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, shell=True)
        for line in self.process_hq.stdout:
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.ffmpeg_time_hq = reg.group(0) if reg else ''

        # command_240p = "ffmpeg -y  -v quiet -stats -i \"" + str(
        #     input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos -s 426x240 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec aac -ab 64k -movflags +faststart \"" + output_240p + "\""
        command_240p = "ffmpeg -y -hwaccel cuda -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos -s 426x240 -profile:v baseline -level 3.0 -vcodec h264_nvenc -crf 27 -r 24 -preset slow -pix_fmt yuv420p -tune film -acodec aac -ab 64k -movflags +faststart \"" + output_240p + "\""
        logging.critical('convert command: ' + command_240p)
        self.process_240p = subprocess.Popen(command_240p, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             universal_newlines=True, shell=True)
        for line in self.process_240p.stdout:
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.ffmpeg_time_240p = reg.group(0) if reg else ''
        return None

    """send command section"""

    def send_convert_command(self, tag):
        password_list = ['1db0046b8b195ee7f40e37963486baf6ed774f803e32049da6956eea3abf532c',
                         'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855']
        if tag in ['rabiea', 'rabiea-480', 'rabiea-sizeless']:
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            if hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest() not in password_list:
                try:
                    toaster = ToastNotifier()
                    toaster.show_toast('Wrong password',
                                       'Wrong password for ' + tag,
                                       icon_path='alaa.ico',
                                       duration=2,
                                       threaded=True)
                except:
                    pass
                finally:
                    return None
        host = 'localhost'
        # host = '192.168.4.2'
        # host = '192.168.5.36'
        queue_name = 'studio-app'
        message = {
            'tag': tag,
            'ip': str(socket.gethostbyname(socket.gethostname())),
            'user_id': str(self.user_id),
            'datetime': str(datetime.datetime.now())
        }
        logging.critical('convert message: ' + json.dumps(message))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=json.dumps(message))
        connection.close()
        try:
            toaster = ToastNotifier()
            toaster.show_toast('Convert Command sent',
                               message['ip'],
                               icon_path='alaa.ico',
                               duration=2,
                               threaded=True)
        except:
            pass


if __name__ == '__main__':
    setup_logging()
    # TODO: fix this backdoor
    # user = attempt_login()
    user = {'id': 27244, 'first_name': 'عرفان', 'last_name': 'قلی زاده', 'name_slug': None, 'mobile': '09305551082',
            'mobile_verified_at': '2020-05-30 14:15:48', 'national_code': '0019451210',
            'photo': 'https://cdn.alaatv.com/upload/images/profile/photo_2019-12-31_21-41-25_20200530094719.jpg?w=100&h=100',
            'province': 'تهران', 'city': 'تهران', 'address': 'تهران', 'postal_code': '1347675363', 'school': 'شریف',
            'email': 'erfantkerfan@yahoo.com', 'bio': None, 'info': None, 'major': {'id': 1, 'name': 'ریاضی'},
            'grade': {'id': 10, 'name': None}, 'gender': {'id': 1, 'name': 'آقا'}, 'profile_completion': 100,
            'wallet_balance': 0, 'updated_at': '2020-07-01 18:55:29', 'created_at': '2018-02-11 11:37:49',
            'edit_profile_url': 'https://alaatv.com/user/editProfile/android/eyJpdiI6IlprdWZuZml4WFwvTmV2MWUzQTBwT3RnPT0iLCJ2YWx1ZSI6IlJwK2U0SlJRWWtqY2lKSlQyYXlSWEtxRmU4SGtDc3BoXC9JdHFsUmhHc0RJPSIsIm1hYyI6IjMyYjYwNDRlYWQ4MjhiYjg3OGY1MmMyY2M2NmVkMWMxNTFkNDFkYWVlMTJlODRiZjNmNDdmZTU2NDVkZjVhOWIifQ==?expires=1597320831&signature=31aed31dc3b3f155e5453feb677dd21b9a0a8573a052b055713d90a370793bf9'}
    # panel = Main(user)
    panel = Main(user)
