import datetime
import hashlib
import json
import logging
import os
import socket
import time
import tkinter as tk
import tkinter.scrolledtext as st
from functools import partial
from tkinter import simpledialog

import paramiko
import pika
import requests
from dotenv import load_dotenv
from win10toast import ToastNotifier


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

        self.x3 = tk.Button(self.root, command=partial(self.onpwdentry, '<Return>'), text='Login')
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

        self.convert_menu = tk.Menu(self.menubar, tearoff=0)
        self.convert_menu.add_command(label='axis', command=partial(self.send_convert_command, 'axis'))
        self.convert_menu.add_command(label='convert', command=partial(self.send_convert_command, 'studio'))
        self.convert_menu.add_command(label='announce', command=partial(self.send_convert_command, 'announce'))
        self.menubar.add_cascade(label='Studio', menu=self.convert_menu)

        self.rabi_menu = tk.Menu(self.menubar, tearoff=0)
        self.rabi_menu.add_command(label='rabiea', command=partial(self.send_convert_command, 'rabiea'))
        self.rabi_menu.add_command(label='rabiea-480', command=partial(self.send_convert_command, 'rabiea-480'))
        self.rabi_menu.add_command(label='rabiea-sizeless',
                                   command=partial(self.send_convert_command, 'rabiea-sizeless'))
        self.menubar.add_cascade(label='Rabiea', menu=self.rabi_menu)

        self.upload_menu = tk.Menu(self.menubar, tearoff=0)
        self.upload_menu.add_command(label='normal', command=partial(self.send_upload_command, 'normal'))
        self.upload_menu.add_command(label='normal force!', command=partial(self.send_upload_command, 'normal_force'))
        self.upload_menu.add_command(label='paid', command=partial(self.send_upload_command, 'paid'))
        self.upload_menu.add_command(label='paid force!', command=partial(self.send_upload_command, 'paid_force'))
        self.menubar.add_cascade(label='Upload', menu=self.upload_menu)

        self.log_menu = tk.Menu(self.menubar, tearoff=0)
        self.log_menu.add_command(label='studio', command=partial(self.get_log, 'app'))
        self.log_menu.add_command(label='upload', command=partial(self.get_log, 'upload'))
        self.menubar.add_cascade(label='Log', menu=self.log_menu)

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

    # def axis(self):
    #     self.file_name = filedialog.askopenfilename(filetypes=(('mkv files', '*.mkv'), ('All files', '*.*')))
    #     if self.file_name == '':
    #         return None
    #     directory = os.path.join(os.path.dirname(self.file_name), 'mp4')
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)
    #     modified_file_name = os.path.join(directory, os.path.basename(self.file_name).replace('mkv', 'mp4'))
    #     thread = threading.Thread(target=self.start_axis, args=(self.file_name, modified_file_name))
    #     self.root.protocol('WM_DELETE_WINDOW', self.root.iconify)
    #     self.welcome_text.pack_forget()
    #     self.root.config(menu='')
    #     self.space = tk.Label(self.root, text=os.linesep * 3)
    #     self.space.pack()
    #     self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
    #     self.progress_bar.pack()
    #     self.root.update()
    #
    #     self.ffmpeg_time = ''
    #     thread.start()
    #     while thread.is_alive():
    #         try:
    #             self.percent_text.pack_forget()
    #         except:
    #             pass
    #         try:
    #             percent = os.path.getsize(modified_file_name) / os.path.getsize(self.file_name) * 100
    #             self.progress_bar['value'] = percent
    #         except:
    #             pass
    #         self.percent_text = tk.Label(self.root, text='مدت زمان تبدیل شده' + os.linesep + self.ffmpeg_time)
    #         self.percent_text.pack()
    #         self.root.update()
    #
    #     os.startfile(directory.replace('/', '\\'))
    #     self.root.protocol('WM_DELETE_WINDOW', self.quit_window)
    #     self.space.pack_forget()
    #     self.progress_bar.pack_forget()
    #     self.percent_text.pack_forget()
    #     self.config_menu()
    #     self.root.update()
    #
    #     toaster = ToastNotifier()
    #     toaster.show_toast('Axis Finished',
    #                        self.file_name,
    #                        icon_path='alaa.ico',
    #                        duration=10,
    #                        threaded=True)
    #     self.root.destroy()
    #     self.__init__(user)
    #
    # def start_axis(self, input, output):
    #     command = "ffmpeg -y -v quiet -stats -i \"" + str(
    #         input) + "\" -metadata title=\"@alaa_sanatisharif\" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"" + output + "\""
    #     logging.critical('axis command: ' + command)
    #     self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    #                                     universal_newlines=True, shell=True)
    #     for line in self.process.stdout:
    #         reg = re.search('\d\d:\d\d:\d\d', line)
    #         self.ffmpeg_time = reg.group(0) if reg else ''
    #     return None

    """convert section"""

    # def convert(self):
    #     self.file_name = filedialog.askopenfilename(filetypes=(('mp4 files', '*.mp4'), ('All files', '*.*')))
    #     regex = re.compile(r'C:\\Alaa\\Finish\\\d{3,4}\\HD_720p')
    #     if self.file_name == '':
    #         return None
    #     elif not regex.match(str(self.file_name).replace('/', '\\')):
    #         toaster = ToastNotifier()
    #         toaster.show_toast('Path Invalid',
    #                            r'select a file in C:\Alaa\Finish',
    #                            icon_path='alaa.ico',
    #                            duration=2,
    #                            threaded=True)
    #         return None
    #
    #     directory_hq = os.path.join(os.path.dirname(os.path.dirname(self.file_name)), 'hq')
    #     if not os.path.exists(directory_hq):
    #         os.makedirs(directory_hq)
    #     directory_240p = os.path.join(os.path.dirname(os.path.dirname(self.file_name)), '240p')
    #     if not os.path.exists(directory_240p):
    #         os.makedirs(directory_240p)
    #
    #     command = "ffprobe -v error -hide_banner -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -i \"" + str(
    #         self.file_name) + "\""
    #     logging.critical('ffprobe command: ' + command)
    #     ffprobe_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    #                                        universal_newlines=True, shell=True)
    #     out, err = ffprobe_process.communicate()
    #     reg = re.search('\d*\.\d*', str(err) + str(out))
    #     self.total_duration = float(reg.group(0)) if reg else parse_seconds('00:15:00')
    #     modified_file_name_hq = os.path.join(directory_hq, os.path.basename(self.file_name))
    #     modified_file_name_240p = os.path.join(directory_240p, os.path.basename(self.file_name))
    #     self.root.protocol('WM_DELETE_WINDOW', self.root.iconify)
    #     thread = threading.Thread(target=self.start_convert,
    #                               args=(self.file_name, modified_file_name_hq, modified_file_name_240p))
    #     self.welcome_text.pack_forget()
    #     self.root.config(menu='')
    #     self.space = tk.Label(self.root, text=os.linesep * 1)
    #     self.space.pack()
    #     self.title_hq = tk.Label(self.root, text='HQ')
    #     self.title_hq.pack()
    #     self.progress_hq = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
    #     self.progress_hq.pack()
    #     self.title_240p = tk.Label(self.root, text='240p')
    #     self.title_240p.pack()
    #     self.progress_240p = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
    #     self.progress_240p.pack()
    #     self.root.update()
    #     self.ffmpeg_time_hq = ''
    #     self.ffmpeg_time_240p = ''
    #     thread.start()
    #     while thread.is_alive():
    #         self.progress_hq['value'] = parse_seconds(self.ffmpeg_time_hq) / self.total_duration * 100
    #         self.progress_240p['value'] = parse_seconds(self.ffmpeg_time_240p) / self.total_duration * 100
    #         self.root.update()
    #
    #     os.startfile(os.path.dirname(self.file_name).replace('/', '\\'))
    #     self.root.protocol('WM_DELETE_WINDOW', self.quit_window)
    #     self.space.pack_forget()
    #     self.title_hq.pack_forget()
    #     self.progress_hq.pack_forget()
    #     self.title_240p.pack_forget()
    #     self.progress_240p.pack_forget()
    #     self.config_menu()
    #     self.root.update()
    #
    #     toaster = ToastNotifier()
    #     toaster.show_toast('Convert Finished',
    #                        self.file_name,
    #                        icon_path='alaa.ico',
    #                        duration=10,
    #                        threaded=True)
    #     self.root.destroy()
    #     self.__init__()
    #
    # def start_convert(self, input, output_hq, output_240p):
    #     # command_hq = "ffmpeg -y  -v quiet -stats -i \"" + str(
    #     #     input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec aac -ab 96k -movflags +faststart \"" + output_hq + "\""
    #     command_hq = "ffmpeg -y -hwaccel cuda -v quiet -stats -i \"" + str(
    #         input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos -s 854x480 -profile:v baseline -level 3.0 -vcodec h264_nvenc -crf 27 -r 24 -preset slow -pix_fmt yuv420p -tune film -acodec aac -ab 96k -movflags +faststart \"" + output_hq + "\""
    #     logging.critical('convert command: ' + command_hq)
    #     self.process_hq = subprocess.Popen(command_hq, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    #                                        universal_newlines=True, shell=True)
    #     for line in self.process_hq.stdout:
    #         reg = re.search('\d\d:\d\d:\d\d', line)
    #         self.ffmpeg_time_hq = reg.group(0) if reg else ''
    #
    #     # command_240p = "ffmpeg -y  -v quiet -stats -i \"" + str(
    #     #     input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos -s 426x240 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec aac -ab 64k -movflags +faststart \"" + output_240p + "\""
    #     command_240p = "ffmpeg -y -hwaccel cuda -v quiet -stats -i \"" + str(
    #         input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos -s 426x240 -profile:v baseline -level 3.0 -vcodec h264_nvenc -crf 27 -r 24 -preset slow -pix_fmt yuv420p -tune film -acodec aac -ab 64k -movflags +faststart \"" + output_240p + "\""
    #     logging.critical('convert command: ' + command_240p)
    #     self.process_240p = subprocess.Popen(command_240p, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    #                                          universal_newlines=True, shell=True)
    #     for line in self.process_240p.stdout:
    #         reg = re.search('\d\d:\d\d:\d\d', line)
    #         self.ffmpeg_time_240p = reg.group(0) if reg else ''
    #     return None

    """send convert section"""

    def send_convert_command(self, tag):
        password_list = ['4b9d51c427c2ec93a40c4c9b08eb1d5ac0cdc6d175e135cc03bac8ba2a5918d3']
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
        host = '192.168.4.2'
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
            toaster.show_toast('Command sent: ' + str(tag),
                               message['ip'],
                               icon_path='alaa.ico',
                               duration=4,
                               threaded=True)
        except:
            pass

    """send upload section"""

    def send_upload_command(self, tag):
        password_list = ['1db0046b8b195ee7f40e37963486baf6ed774f803e32049da6956eea3abf532c']
        if tag in ['normal_force', 'paid_force']:
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
        host = '192.168.4.2'
        queue_name = 'studio-upload'
        message = {
            'tag': tag,
            'ip': str(socket.gethostbyname(socket.gethostname())),
            'user_id': str(self.user_id),
            'datetime': str(datetime.datetime.now())
        }
        logging.critical('upload message: ' + json.dumps(message))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=json.dumps(message))
        connection.close()
        try:
            toaster = ToastNotifier()
            toaster.show_toast('Upload sent: ' + str(tag),
                               message['ip'],
                               icon_path='alaa.ico',
                               duration=4,
                               threaded=True)
        except:
            pass

    def get_log(self, tag):
        host = '192.168.4.2'
        command = 'journalctl --no-pager -n 20 --output=cat -u studio-' + str(tag)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username='film', password=PASSWORD)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

        try:
            self.log_win.destroy()
        except:
            pass
        self.log_win = tk.Tk()
        self.log_win.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.log_win.title('Alaa studio app log')

        buttons_frame = tk.Frame(self.log_win)
        buttons_frame.grid(row=0, column=0, sticky=tk.W + tk.E)

        if tag == 'app':
            btn_Image = tk.Button(buttons_frame, command=partial(self.get_log, 'app'), text='Refresh')
            btn_Image.grid(row=0, column=0, padx=10, pady=10)
        elif tag == 'upload':
            btn_Image = tk.Button(buttons_frame, command=partial(self.get_log, 'upload'), text='Refresh')
            btn_Image.grid(row=0, column=0, padx=10, pady=10)

        # Group1 Frame ----------------------------------------------------
        self.group1 = tk.LabelFrame(self.log_win, text="Log Box", padx=5, pady=5)
        self.group1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E + tk.W + tk.N + tk.S)

        self.log_win.columnconfigure(0, weight=1)
        self.log_win.rowconfigure(1, weight=1)

        self.group1.rowconfigure(0, weight=1)
        self.group1.columnconfigure(0, weight=1)

        # Create the textbox
        self.txtbox = st.ScrolledText(self.group1, width=125, height=25)
        self.txtbox.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        lines = ssh_stdout.readlines()
        ansi_chars = ['\x1b[0m', '\x1b[1m', '\x1b[4m', '\x1b[7m', '\x1b[30m', '\x1b[31m', '\x1b[32m', '\x1b[33m',
                      '\x1b[34m', '\x1b[35m', '\x1b[36m', '\x1b[37m']
        ls = []
        for line in lines:
            temp = line
            for ansi in ansi_chars:
                temp = temp.replace(ansi, '')
            ls.append(temp)
        self.txtbox.insert(tk.INSERT, ''.join(ls))
        self.txtbox.configure(state='disabled')

        tk.mainloop()


if __name__ == '__main__':
    load_dotenv()
    PASSWORD = os.getenv("PASSWORD_FILM")
    setup_logging()
    user = attempt_login()
    panel = Main(user)
