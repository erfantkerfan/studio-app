import logging
import subprocess
import time
import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import requests
import json
import os
import re
import threading
from win10toast import ToastNotifier


class Insert(object):

    def __init__(self, name):
        self.root = tk.Tk()
        self.add_menu()
        self.init_window(' ' + name)
        self.load_content_view()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        self.root.mainloop()

    def load_content_view(self):
        self.load_browser()
        self.load_thumbnail()
        self.load_canvas()
        self.load_subtitle()
        self.load_description()
        self.load_tag()
        self.load_set()
        self.load_order()
        self.load_payment()
        self.load_contenttype()
        self.load_teacher_id()

    def load_teacher_id(self):
        self.vars6 = tk.StringVar()
        self.vars6.trace('w', self.validate6)
        self.labelText = tk.StringVar()
        self.labelText.set("آیدی دبیر")
        self.labelDir = tk.Label(self.root, textvariable=self.labelText)
        self.labelDir.pack()
        self.browser6 = tk.Entry(self.root, width=10, justify='center', textvariable=self.vars6)
        self.browser6.pack()

    def load_contenttype(self):
        self.type_var = tk.StringVar(self.root)
        self.type_var.set("فیلم")  # default value
        self.x = tk.OptionMenu(self.root, self.type_var, "فیلم", "جزوه")
        self.x.config(state='disable')
        self.x.pack()

    def load_set(self):
        self.vars3 = tk.StringVar()
        self.vars3.trace('w', self.validate3)
        self.labelText = tk.StringVar()
        self.labelText.set("شماره ست")
        self.labelDir = tk.Label(self.root, textvariable=self.labelText)
        self.labelDir.pack()
        self.browser3 = tk.Entry(self.root, width=5, justify='center', textvariable=self.vars3)
        self.browser3.pack()

    def load_payment(self):
        self.check_value = tk.IntVar()
        self.check_value.set(1)
        a = tk.Checkbutton(self.root, text="رایگان", variable=self.check_value, state='disabled')
        a.pack()

    def load_order(self):
        self.vars4 = tk.StringVar()
        self.vars4.trace('w', self.validate4)
        self.labelText = tk.StringVar()
        self.labelText.set("شماره جلسه")
        self.labelDir = tk.Label(self.root, textvariable=self.labelText)
        self.labelDir.pack()
        self.browser4 = tk.Entry(self.root, width=5, justify='center', textvariable=self.vars4)
        self.browser4.pack()

    def load_tag(self):
        self.labelText = tk.StringVar()
        self.labelText.set("تگ")
        self.labelDir = tk.Label(self.root, textvariable=self.labelText)
        self.labelDir.pack()
        self.browser5 = tk.Text(self.root, height=3, width=60)
        self.browser5.pack()

    def load_description(self):
        self.labelText = tk.StringVar()
        self.labelText.set("توضیحات")
        self.labelDir = tk.Label(self.root, textvariable=self.labelText)
        self.labelDir.pack()
        self.browser2 = tk.Text(self.root, height=7, width=60)
        self.browser2.pack()

    def load_subtitle(self):
        self.labelText = tk.StringVar()
        self.labelText.set("زیرنویس")
        self.labelDir = tk.Label(self.root, textvariable=self.labelText)
        self.labelDir.pack()
        self.browser2 = tk.Text(self.root, height=1, width=60)
        self.browser2.pack()

    def load_canvas(self):
        self.canvas = tk.Canvas(self.root, width=int(200) + 30, height=int(720 / 1280 * 200) + 30)
        self.canvas.pack()

    def load_thumbnail(self):
        self.thumbnail = tk.Entry(self.root, width=60, justify='center')
        self.thumbnail.config(state='disabled')
        self.thumbnail.pack()

    def load_browser(self):
        self.browser = tk.Entry(self.root, width=60, justify='center')
        self.browser.config(state='disabled')
        self.browser.pack()

    def validate3(self, *args):
        if not self.vars3.get().isnumeric() or not len(self.vars3.get()) > 4:
            corrected = ''.join(filter(str.isnumeric, self.vars3.get()[0:3]))
            self.vars3.set(corrected)

    def validate4(self, *args):
        if not self.vars4.get().isnumeric() or not len(self.vars4.get()) > 4:
            corrected = ''.join(filter(str.isnumeric, self.vars4.get()[0:3]))
            self.vars4.set(corrected)

    def validate6(self, *args):
        if not self.vars6.get().isnumeric():
            corrected = ''.join(filter(str.isnumeric, self.vars6.get()))
            self.vars6.set(corrected)

    def browser_mp4(self):
        self.file_name = filedialog.askopenfilename(filetypes=(("mp4 files", "*.mp4"), ("All files", "*.*")))
        self.browser_edit()

    def browser_thumbnail(self):
        self.file_thumbnail = filedialog.askopenfilename(filetypes=(("jpg files", "*.jpg"), ("All files", "*.*")))
        self.thumbnail_edit()
        self.thumbnail_view()

    def thumbnail_view(self):
        self.image = Image.open(self.file_thumbnail)
        self.image = self.image.resize((int(200), int(720 / 1280 * 200)), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(20, 20, anchor=tk.NW, image=self.img)

    def browser_edit(self):
        self.browser.config(state='normal')
        self.browser.delete(0, tk.END)
        self.browser.insert(tk.INSERT, self.file_name)
        self.browser.config(state='disabled')

    def thumbnail_edit(self):
        self.thumbnail.config(state='normal')
        self.thumbnail.delete(0, tk.END)
        self.thumbnail.insert(tk.INSERT, self.file_thumbnail)
        self.thumbnail.config(state='disabled')

    def init_window(self, name):
        self.root.geometry("500x700")
        self.root.resizable(height=None, width=None)
        self.root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.root.title('Alaa studio app' + name)

    def add_menu(self):
        self.menubar = tk.Menu(self.root)
        self.add_voice("Convert", self.browser_mp4)
        self.add_voice("Thumbnail", self.browser_thumbnail)
        self.add_voice("Quit", self.quit_window)
        self.config_menu()

    def add_voice(self, label, command):
        """Add a voice to menubar"""
        self.menubar.add_command(label=label, command=command)

    def config_menu(self):
        """Make the menu visible"""
        self.root.config(menu=self.menubar)

    def print_hello(self):
        """called clicking on hello menubar hello voice"""
        print("hello!")

    def quit_window(self):
        """called by quit menubar label voice"""
        self.root.destroy()
        os._exit(0)


class Main(object):

    def __init__(self):
        self.root = tk.Tk()
        self.add_menu()
        self.init_window()
        self.load_landing()
        self.root.mainloop()

    def onpwdentry(self, event):
        self.password = self.pwdbox.get()
        self.mobile = self.mblbox.get()
        self.root.destroy()

    def onokclick(self):
        self.mobile = self.mblbox.get()
        self.password = self.pwdbox.get()
        self.root.destroy()

    def start_axis(self, input, output):
        command = "ffmpeg -y  -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"" + output + "\""
        logging.critical('axis command: ' + command)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True, shell=True)
        for line in self.process.stdout:
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.x = reg.group(0) if reg else ''

    def axis(self):
        self.file_name = filedialog.askopenfilename(filetypes=(("mkv files", "*.mkv"), ("All files", "*.*")))
        if self.file_name == "":
            return None
        directory = os.path.join(os.path.dirname(self.file_name), 'mp4')

        if not os.path.exists(directory):
            os.makedirs(directory)

        modified_file_name = os.path.join(directory, os.path.basename(self.file_name).replace('mkv', 'mp4'))
        t = self.load_loading(modified_file_name)
        self.x = ''
        t.start()
        while t.is_alive():
            try:
                self.percent.pack_forget()
            except:
                pass
            try:
                percent = os.path.getsize(modified_file_name) / os.path.getsize(self.file_name) * 100
                self.progress['value'] = percent
            except:
                pass
            self.percent = tk.Label(self.root, text='مدت زمان تبدیل شده' + os.linesep + self.x)
            self.percent.pack()
            self.root.update()
        os.startfile(directory)
        try:
            self.load_landing()
        except:
            pass
        self.process.terminate()
        del t

        toaster = ToastNotifier()
        toaster.show_toast("Axis Finished",
                           self.file_name,
                           icon_path='alaa.ico',
                           duration=10,
                           threaded=True)
        self.root.destroy()
        self.__init__()

    def start_convert(self, input, output_hq, output_240p):
        # TODO libfdk_aac
        # command_hq = "ffmpeg -y  -v quiet -stats -i \"" + str(
        #     input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec aac -ab 96k -movflags +faststart \"" + output_hq + "\""
        command_hq = "ffmpeg -y -hwaccel cuda -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 -vcodec h264_nvenc -crf 27 -r 24 -pix_fmt yuv420p -tune film -acodec aac -ab 96k -movflags +faststart \"" + output_hq + "\""
        logging.critical('convert command: ' + command_hq)
        self.process_hq = subprocess.Popen(command_hq, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, shell=True)
        for line in self.process_hq.stdout:
            # print(line)
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.x_hq = reg.group(0) if reg else ''

        # command_240p = "ffmpeg -y  -v quiet -stats -i \"" + str(
        #     input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos  -s 426x240 -profile:v baseline -level 3.0 -vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec aac -ab 64k -movflags +faststart \"" + output_240p + "\""
        command_240p = "ffmpeg -y -hwaccel cuda -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -sws_flags lanczos  -s 426x240 -profile:v baseline -level 3.0 -vcodec h264_nvenc -crf 27 -r 24 -pix_fmt yuv420p -tune film -acodec aac -ab 64k -movflags +faststart \"" + output_240p + "\""
        logging.critical('convert command: ' + command_240p)
        self.process_240p = subprocess.Popen(command_240p, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             universal_newlines=True, shell=True)
        for line in self.process_240p.stdout:
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.x_240p = reg.group(0) if reg else ''

    def convert(self):
        self.file_name = filedialog.askopenfilename(filetypes=(("mp4 files", "*.mp4"), ("All files", "*.*")))
        if self.file_name == "":
            return None

        directory_hq = os.path.join(os.path.dirname(os.path.dirname(self.file_name)), 'hq')
        if not os.path.exists(directory_hq):
            os.makedirs(directory_hq)
        directory_240p = os.path.join(os.path.dirname(os.path.dirname(self.file_name)), '240p')
        if not os.path.exists(directory_240p):
            os.makedirs(directory_240p)

        # command = "ffprobe -hide_banner -i \"" + str(self.file_name) + "\""
        command = "ffprobe -v error -hide_banner -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -i \"" + str(
            self.file_name) + "\""
        logging.critical('ffprobe command: ' + command)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, shell=True)
        out, err = p.communicate()
        reg = re.search('\d*\.\d*', str(err) + str(out))
        self.duration = float(reg.group(0)) if reg else self.parse_seconds("00:20:00")

        modified_file_name_hq = os.path.join(directory_hq, os.path.basename(self.file_name))
        modified_file_name_240p = os.path.join(directory_240p, os.path.basename(self.file_name))
        t = self.load_loading_2(modified_file_name_hq, modified_file_name_240p)
        self.x_hq = ''
        self.x_240p = ''
        t.start()
        while t.is_alive():
            # try:
            #     self.percent.pack_forget()
            # except:
            #     pass
            # self.percent = tk.Label(self.root, text='مدت زمان تبدیل شده' + os.linesep + self.x_hq)
            # self.percent.pack()
            self.progress_hq['value'] = self.parse_seconds(self.x_hq) / self.duration * 100
            self.progress_240p['value'] = self.parse_seconds(self.x_240p) / self.duration * 100
            # print(self.parse_seconds(self.x_hq))
            # print(self.parse_seconds(self.x_240p))
            # print(self.parse_seconds(self.x_hq) / self.duration * 100)
            # print(self.parse_seconds(self.x_240p) / self.duration * 100)
            # print(self.duration)
            # print('*' * 20)
            self.root.update()
        os.startfile(os.path.dirname(self.file_name).replace('/', '\\'))
        try:
            self.load_landing_2()
        except:
            pass

        toaster = ToastNotifier()
        toaster.show_toast("Convert Finished",
                           self.file_name,
                           icon_path='alaa.ico',
                           duration=10,
                           threaded=True)
        self.root.destroy()
        self.__init__()

    def parse_seconds(self, t):
        if t in ['', ' ', None]:
            return 0
        tx = time.strptime(t, '%H:%M:%S')
        seconds = datetime.timedelta(hours=tx.tm_hour, minutes=tx.tm_min, seconds=tx.tm_sec).total_seconds()
        return seconds

    def load_login(self):
        self.load_content_view()
        self.loading.pack_forget()
        self.config_menu()
        self.x1.pack()
        self.mblbox.pack()
        self.x2.pack()
        self.pwdbox.pack()
        self.x3.pack()
        self.root.update()

    def load_landing(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        try:
            self.loading.pack_forget()
            self.progress.pack_forget()
            self.percent.pack_forget()
        except:
            pass
        self.config_menu()
        self.loading = tk.Label(self.root, text=os.linesep * 3 + 'سلام آلایی عزیز')
        self.loading.pack()
        self.root.update()

    def load_landing_2(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        try:
            self.progress_240p.pack_forget()
            self.progress_hq.pack_forget()
            self.loading.pack_forget()
            self.percent.pack_forget()
        except:
            pass
        self.config_menu()
        self.loading = tk.Label(self.root, text=os.linesep * 3 + 'سلام آلایی عزیز')
        self.loading.pack()
        self.root.update()

    def load_loading(self, modified_file_name):
        self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        t = threading.Thread(target=self.start_axis, args=(self.file_name, modified_file_name))
        try:
            self.loading.pack_forget()
            self.mblbox.pack_forget()
            self.pwdbox.pack_forget()
            self.x1.pack_forget()
            self.x2.pack_forget()
            self.x3.pack_forget()
        except:
            pass
        self.root.config(menu="")
        self.loading = tk.Label(self.root, text=os.linesep * 3)
        self.loading.pack()
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack()
        self.root.update()
        return t

    def load_loading_2(self, modified_file_name_hq, modified_file_name_240p):
        self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        t = threading.Thread(target=self.start_convert,
                             args=(self.file_name, modified_file_name_hq, modified_file_name_240p))
        try:
            self.loading.pack_forget()
            self.mblbox.pack_forget()
            self.pwdbox.pack_forget()
            self.x1.pack_forget()
            self.x2.pack_forget()
            self.x3.pack_forget()
        except:
            pass
        self.root.config(menu="")
        self.loading = tk.Label(self.root, text=os.linesep * 1)
        self.loading.pack()
        self.title1 = tk.Label(self.root, text='HQ')
        self.title1.pack()
        self.progress_hq = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_hq.pack()
        self.title2 = tk.Label(self.root, text='240p')
        self.title2.pack()
        self.progress_240p = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_240p.pack()
        self.root.update()
        return t

    def load_content_view(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        try:
            self.mblbox.pack_forget()
            self.pwdbox.pack_forget()
            self.x1.pack_forget()
            self.x2.pack_forget()
            self.x3.pack_forget()
        except:
            pass
        self.mblbox = tk.Entry(self.root)
        self.pwdbox = tk.Entry(self.root, show='*')

        self.x1 = tk.Label(self.root, text='mobile')
        self.x1.pack(side='top')
        self.mblbox.pack(side='top')

        self.x2 = tk.Label(self.root, text='password')
        self.x2.pack(side='top')

        self.pwdbox.pack(side='top')
        self.pwdbox.bind('<Return>', self.onpwdentry)

        self.x3 = tk.Button(self.root, command=self.onokclick, text='Login')
        self.x3.pack(side='top')

    def init_window(self):
        self.root.geometry("400x300")
        self.root.resizable(height=None, width=None)
        self.root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.root.title('Alaa studio app')

    def add_menu(self):
        self.menubar = tk.Menu(self.root)
        self.add_voice("Axis", self.axis)
        # self.add_voice("Convert", self.load_login)
        self.add_voice("Convert", self.convert)
        self.add_voice("Quit", self.quit_window)
        self.config_menu()

    def add_voice(self, label, command):
        """Add a voice to menubar"""
        self.menubar.add_command(label=label, command=command)

    def config_menu(self):
        """Make the menu visible"""
        self.root.config(menu=self.menubar)

    def quit_window(self):
        """called by quit menubar label voice"""
        self.root.destroy()
        os._exit(0)


def setup_logging():
    if not os.path.exists('log.txt'):
        with open('log.txt', 'w+') as logfile:
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


def setup_login_request():
    global url, status_code, headers
    url = "http://m.alaatv.com/api/v2/login"
    status_code = None
    headers = {
        'Accept': 'application/json',
        'Cookie': 'nocache=1',
        'Accept-Encoding': 'utf-8'
    }


def send_login_request():
    global status_code, name
    while status_code != 200:
        credentials = Main()
        payload = {'mobile': credentials.mobile,
                   'password': credentials.password,
                   }
        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            status_code = response.status_code
            x = json.loads(response.content)
        except:
            status_code = None
        try:
            if str(x['data']['user']['first_name']) == "None":
                status_code = None
                user_id = None
            else:
                name = str(x['data']['user']['first_name']) + ' ' + str(x['data']['user']['last_name'])
                user_id = str(x['data']['user']['id'])
        except:
            name = "کاربر ناشناس"
            user_id = "Unknown"
        logging.critical("logged in user_id: " + user_id)


if __name__ == '__main__':
    setup_logging()
    setup_login_request()
    send_login_request()
    w = Insert(name)
