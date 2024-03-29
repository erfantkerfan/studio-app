import datetime
import hashlib
import json
import logging
import os
import platform
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.scrolledtext as st
import tkinter.ttk as ttk
import webbrowser
from functools import partial
from tkinter import simpledialog

import paramiko
import pika
import requests
from dotenv import load_dotenv

if platform.system().lower().startswith('win'):
    from win10toast import ToastNotifier
elif platform.system().lower().startswith('lin'):
    import notify2

    notify2.init('studio-app')

VERSION = '2.2.0'
LOG_PATH = '/var/www/studio-app/supervisor-'

def setup_logging():
    if not os.path.exists('log.log'):
        with open('log.log', 'w+') as _:
            pass

    with open('log.log', 'r+') as logfile:
        content = logfile.readlines()
        content = content[-1000:]
        logfile.seek(0)
        logfile.writelines(content)
        logfile.truncate()

    logging.basicConfig(filename='log.log',
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
            continue
        try:
            if str(data['data']['user']['first_name']) == "None":
                status_code = None
                user_id = None
            else:
                user_id = str(data['data']['user']['id'])
        except:
            continue
    logging.critical("logged in user_id: " + user_id)
    return data['data']['user']


def update():
    global root

    def progress():
        while progress:
            if progress_bar['value'] > 100:
                progress_bar['value'] = 0
            progress_bar['value'] += 1
            time.sleep(0.01)

    root = tk.Tk()
    root.geometry("250x150")
    root.resizable(height=None, width=None)
    if platform.system().lower().startswith('win'):
        root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
    # root.protocol('WM_DELETE_WINDOW', root.iconify)
    root.title('Alaa studio app')
    update_title = tk.Label(root, text='در حال بروزرسانی از اینترنت')
    update_title.pack(pady=20)
    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
    progress_bar.pack(pady=10)
    t = threading.Thread(target=progress)
    progress = 1
    t.start()
    root.mainloop()


def get_ip(lookup='192.168.4.3', port=80):
    if platform.system().lower().startswith('win'):
        ip = str(socket.gethostbyname(socket.gethostname()))
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((lookup, port))
        ip = s.getsockname()[0]
        s.close()
    return str(ip)


class Insert(object):

    def __init__(self, root):
        root.withdraw()
        self.window = tk.Tk()
        self.window.protocol('WM_DELETE_WINDOW', self.quit_window)
        self.add_menu()
        self.init_window()

        self.IPS = [
            '192.168.0.15',
            '192.168.0.25',
            '192.168.0.30',
            '192.168.0.51',
            '192.168.0.52',
            '192.168.0.55',
            '192.168.0.68',
            '192.168.0.70',
            '192.168.0.89',
            '192.168.5.33',
            '192.168.5.36',
        ]
        self.reciever = tk.StringVar(self.window)
        options = tk.OptionMenu(self.window, self.reciever, *self.IPS)
        options.pack()

        self.message = tk.StringVar(self.window)
        self.message.set('')
        self.message.trace('w', self.validate)
        self.message_box = tk.Entry(self.window, textvariable=self.message, justify='center', width=90)
        self.message_box.pack(pady=10)
        self.message_box.bind('<Return>', self.send_message)

        self.window.mainloop()

    def validate(self, enevt, *args):
        if len(self.message.get()) > 100:
            self.message.set(self.message.get()[0:100])

    def send_message(self, event):
        host = '192.168.4.3'
        sender = get_ip()
        message = {
            'tag': 'text',
            'text': self.message.get(),
            'sender': sender,
            'ip': sender,
            'user_id': 0,
            'datetime': str(datetime.datetime.now())
        }
        queue_name = self.reciever.get()
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        connection.close()
        self.quit_window()

    def init_window(self):
        self.window.geometry("600x100")
        self.window.resizable(height=None, width=None)
        if platform.system().lower().startswith('win'):
            self.window.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.window.title('Alaa studio app')

    def add_menu(self):
        self.menubar = tk.Menu(self.window)
        self.add_voice("Quit", self.quit_window)
        self.window.config(menu=self.menubar)

    def add_voice(self, label, command):
        """Add a voice to menubar"""
        self.menubar.add_command(label=label, command=command)

    def quit_window(self):
        """called by quit menubar label voice"""
        self.window.destroy()
        self.window.quit()


class InstantMessenger(threading.Thread):
    def __init__(self, user):
        super(InstantMessenger, self).__init__()
        self._is_interrupted = False
        self.host = '192.168.4.3'
        self.name = user['first_name'] + ' ' + user['last_name']
        self.queue_name = get_ip()
        if platform.system().lower().startswith('win'):
            self.spawn = ToastNotifier()
        elif platform.system().lower().startswith('lin'):
            self.spawn = notify2.init('studip-app')

    def stop(self):
        self._is_interrupted = True

    def toaster(self, message):
        try:
            title = 'from ' + message['sender'] + ' :'
            body = message['text']
            if platform.system().lower().startswith('win'):
                self.spawn.show_toast(title, body, icon_path='alaa.ico', duration=60, threaded=True)
            elif platform.system().lower().startswith('lin'):
                n = notify2.Notification(title, body)
                n.show()
        except:
            pass

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)

    def run(self):
        try:
            while True:
                threads = []
                self.connect()
                for message in self.channel.consume(self.queue_name, inactivity_timeout=1):
                    if self._is_interrupted:
                        self.connection.close()
                        break
                    if not message[0]:
                        continue
                    method, properties, body = message
                    self.channel.basic_ack(delivery_tag=method.delivery_tag)
                    message = json.loads(body)
                    threads.append(threading.Thread(target=self.toaster, args=[message], daemon=True))
                    threads[-1].start()
        except:
            pass


class Login(object):
    def __init__(self):
        self.root = tk.Tk()
        self.add_menu()
        self.init_window()
        self.load_landing()
        self.root.mainloop()

    def add_menu(self):
        self.menubar = tk.Menu(self.root)

        self.about_menu = tk.Menu(self.menubar, tearoff=0)
        self.about_menu.add_command(label='update', command=reload)
        chnagelog_url = 'https://github.com/erfantkerfan/studio-app'
        self.about_menu.add_command(label='V ' + VERSION, command=partial(webbrowser.open, chnagelog_url, new=1))
        self.menubar.add_cascade(label='About', menu=self.about_menu)

        self.add_voice("Quit", self.quit_window)

        self.config_menu()

    def init_window(self):
        self.root.geometry("250x150")
        self.root.resizable(height=None, width=None)
        if platform.system().lower().startswith('win'):
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
        self.root.protocol('WM_DELETE_WINDOW', self.quit_window)
        self.add_menu()
        self.init_window()
        self.config_menu()
        self.load_landing()
        self.root.mainloop()

    def load_landing(self):
        self.welcome_text = tk.Label(self.root, text=os.linesep * 3 + 'سلام ' + user['first_name'] + ' ' + user[
            'last_name'] + ' عزیز' + os.linesep * 3 + get_ip())
        self.welcome_text.pack()
        self.root.update()

    def init_window(self):
        self.root.geometry("400x300")
        self.root.resizable(height=None, width=None)
        if platform.system().lower().startswith('win'):
            self.root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.root.title('Alaa studio app')

    def add_menu(self):
        self.menubar = tk.Menu(self.root)

        self.convert_menu = tk.Menu(self.menubar, tearoff=0)
        self.convert_menu.add_command(label='axis', command=partial(self.send_convert_command, 'axis'))
        self.convert_menu.add_command(label='convert', command=partial(self.send_convert_command, 'convert'))
        self.convert_menu.add_command(label='tablet', command=partial(self.send_convert_command, 'tablet'))
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
        self.upload_menu.add_command(label='paid', command=partial(self.send_upload_command, 'paid'))
        self.upload_menu.add_command(label='pamphlet', command=partial(self.send_upload_command, 'pamphlet'))
        self.upload_menu.add_command(label='introVideo', command=partial(self.send_upload_command, 'introVideo'))
        self.menubar.add_cascade(label='Upload', menu=self.upload_menu)

        self.log_menu = tk.Menu(self.menubar, tearoff=0)
        self.log_menu.add_command(label='axis', command=partial(self.get_log, 'axis'))
        self.log_menu.add_command(label='convert', command=partial(self.get_log, 'convert'))
        self.log_menu.add_command(label='upload', command=partial(self.get_log, 'upload'))
        self.menubar.add_cascade(label='Log', menu=self.log_menu)

        self.add_voice('Message', self.message_box)

        self.about_menu = tk.Menu(self.menubar, tearoff=0)
        self.about_menu.add_command(label='update', command=reload)
        chnagelog_url = 'https://github.com/erfantkerfan/studio-app'
        self.about_menu.add_command(label='V ' + VERSION, command=partial(webbrowser.open, chnagelog_url, new=1))
        self.menubar.add_cascade(label='About', menu=self.about_menu)

        self.add_voice('Quit', self.quit_window)
        self.config_menu()

    def message_box(self):
        Insert(self.root)
        self.root.deiconify()

    def add_voice(self, label, command):
        self.menubar.add_command(label=label, command=command)

    def config_menu(self):
        self.root.config(menu=self.menubar)

    def quit_window(self):
        self.root.destroy()
        im.stop()
        os._exit(0)

    """send convert section"""

    def send_convert_command(self, tag):
        password_list = ['4b9d51c427c2ec93a40c4c9b08eb1d5ac0cdc6d175e135cc03bac8ba2a5918d3']
        priority = 0
        if tag in ['rabiea', 'rabiea-480', 'rabiea-sizeless']:
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            priority = 1
            if hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest() not in password_list:
                try:
                    title = 'Wrong password'
                    body = 'Wrong password for ' + tag
                    if platform.system().lower().startswith('win'):
                        toaster = ToastNotifier()
                        toaster.show_toast(title,
                                           body,
                                           icon_path='alaa.ico',
                                           duration=2,
                                           threaded=True)
                    elif platform.system().lower().startswith('lin'):
                        n = notify2.Notification(title, body)
                        n.show()
                except:
                    pass
                finally:
                    return None
        host = '192.168.4.3'
        queue_name = 'studio-convert'
        if tag in ['axis']:
            queue_name = 'studio-axis'
        message = {
            'tag': tag,
            'ip': get_ip(),
            'user_id': str(self.user_id),
            'datetime': str(datetime.datetime.now())
        }
        logging.critical('convert message: ' + json.dumps(message))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=json.dumps(message),
                              properties=pika.BasicProperties(priority=priority))
        connection.close()
        try:
            toaster = ToastNotifier()
            toaster.show_toast('Command sent: ' + str(tag),
                               message['ip'],
                               icon_path='alaa.ico',
                               duration=60,
                               threaded=True)
        except:
            pass

    """send upload section"""

    def send_upload_command(self, tag):
        host = '192.168.4.3'
        queue_name = 'studio-upload'
        message = {
            'tag': tag,
            'ip': get_ip(),
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
                               duration=60,
                               threaded=True)
        except:
            pass

    """show log section"""

    def get_log(self, tag):
        host = '192.168.4.3'
        command = 'tail -n 20 ' + LOG_PATH + str(tag) + '.log'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username='alaa', password=PASSWORD)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=0))
        count_channel = connection.channel()
        q = count_channel.queue_declare(queue='studio-' + tag)
        count = q.method.message_count
        try:
            self.log_win.destroy()
        except:
            pass
        self.log_win = tk.Tk()
        if platform.system().lower().startswith('win'):
            self.log_win.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.log_win.title('Alaa studio-app log')

        buttons_frame = tk.Frame(self.log_win)
        buttons_frame.grid(row=0, column=0, sticky=tk.W + tk.E)

        btn_Log = tk.Button(buttons_frame, command=partial(self.get_log, str(tag)),
                            text='Refresh ---> ' + str(count) + ' in queue', fg='red')
        btn_Log.grid(row=0, column=0, padx=10, pady=10)

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


# reload the app with needed sys arguments
def reload(updated=False):
    if updated:
        os.execv(sys.executable, ['python ' + str(__file__) + ' updated'])
    else:
        os.execv(sys.executable, ['python ' + str(__file__)])


if __name__ == '__main__':
    # try to update app from github
    load_dotenv()
    DEBUG = bool(os.getenv("DEBUG"))
    if DEBUG or (len(sys.argv) > 1 and sys.argv[1] == 'updated'):
        PASSWORD = os.getenv("PASSWORD_ALAA")
        setup_logging()
        user = attempt_login()
        # from erfan import user
        im = InstantMessenger(user)
        im.start()
        # run main app
        panel = Main(user)
    else:
        tt = threading.Thread(target=update)
        tt.start()

        command = 'git fetch --all'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        status = process.wait()

        if status == 0:
            update_text = tk.StringVar()
            update_text.set('✔')
            update_label = tk.Label(root, textvariable=update_text, fg='green')
            update_label.pack(pady=5)
            GIT_REMOTE = 'origin'
            GIT_BRANCH = 'master'
            command = 'git reset --hard ' + GIT_REMOTE + '/' + GIT_BRANCH
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            status = process.wait()
            if status == 0:
                update_text.set('✔ ✔')
                command = 'pip install -r requirements.txt'
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
                status = process.wait()
                if status == 0:
                    update_text.set('✔ ✔ ✔')
                    reload(updated=True)

        root.quit()
        os._exit(0)
