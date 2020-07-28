import logging
import subprocess
import time
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import requests
import json
import os
import threading


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
        self.type_var = StringVar(self.root)
        self.type_var.set("فیلم")  # default value
        self.x = OptionMenu(self.root, self.type_var, "فیلم", "جزوه")
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
        self.check_value = IntVar()
        self.check_value.set(1)
        a = Checkbutton(self.root, text="رایگان", variable=self.check_value, state='disabled')
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
        command = "ffmpeg -y -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"" + output + "\""
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # logging.critical('axis command: ' + command)
        # self.result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si,
        #                              shell=True)
        # self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        #                                 universal_newlines=True, startupinfo=si, shell=True)
        self.process = subprocess.call(command, startupinfo=si, shell=True)

    def axis(self):
        self.file_name = filedialog.askopenfilename(filetypes=(("mkv files", "*.mkv"), ("All files", "*.*")))
        if self.file_name == "":
            return None
        directory = os.path.join(os.path.dirname(self.file_name), 'mp4')

        if not os.path.exists(directory):
            os.makedirs(directory)

        modified_file_name = os.path.join(directory, os.path.basename(self.file_name).replace('mkv', 'mp4'))
        t = self.load_loading(modified_file_name)
        # print('here')
        t.start()
        # time.sleep(1)

        time.sleep(0.1)
        while t.is_alive():
            try:
                # for line in self.process.stdout:
                #     print(line)
                # reg = re.search('\d\d:\d\d:\d\d', self.result)
                # x = reg.group(0) if reg else ''

                # print(self.result)
                # print(self.result.check_returncode())
                # time.sleep(0.1)
                # print(line for line in self.process.stdout)
                # print(dir(self.process.stdout))
                # print(self.process.stdout)
                time.sleep(0.005)
                percent = os.path.getsize(modified_file_name) / os.path.getsize(self.file_name) * 100
                try:
                    self.percent.pack_forget()
                except:
                    pass
                self.percent = tk.Label(self.root, text=str(int(percent)) + '%')
                self.percent.pack()
                self.progress['value'] = percent
                self.root.update()
            except:
                pass
        # t.join()
        os.startfile(directory)
        try:
            self.load_landing()
        except:
            pass

    # TODO
    # def start_convert(self, input, output):
    #     command = "ffmpeg -y -i \"" + str(
    #         input) + "\" -metadata title=\"@alaa_sanatisharif\" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"" + output + "\""
    #     si = subprocess.STARTUPINFO()
    #     si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    #     logging.critical('axis command: ' + command)
    #     subprocess.call(command, startupinfo=si)
    #     os.startfile(os.path.dirname(output))

    # TODO
    # def convert(self):
    #     command = 'ffmpeg -y -i "C:/Users/Erfan/Desktop/test/2020-07-23ArashAdabiyat-HosenKhani(5).mkv" -metadata title="@alaa_sanatisharif" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 "C:/Users/Erfan/Desktop/test/mp4/2020-07-23ArashAdabiyat-HosenKhani(5).mp4'
    #     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #     for line in process.stdout:
    #         print(line)
    #         print('-' * 50)

    # self.file_name = filedialog.askopenfilename(filetypes=(("mp4 files", "*.mp4"), ("All files", "*.*")))
    # if self.file_name == "":
    #     return None
    # directory = os.path.join(os.path.dirname(self.file_name), 'mp4')
    #
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    #
    # modified_file_name = os.path.join(directory, os.path.basename(self.file_name).replace('mkv', 'mp4'))
    # t = self.load_loading(modified_file_name)
    # t.start()
    #
    # while t.is_alive():
    #     try:
    #         self.root.update()
    #     except:
    #         pass
    # try:
    #     self.load_landing()
    # except:
    #     pass

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
        self.loading = tk.Label(self.root, text=os.linesep * 1 + 'welcome!')
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
        # self.loading = tk.Label(self.root, text=os.linesep * 2 + 'wait for axis to finish ...')
        self.loading = tk.Label(self.root, text=os.linesep * 1)
        self.loading.pack()
        # self.loading.pack()
        self.progress = ttk.Progressbar(self.root, orient=HORIZONTAL, length=150, mode='determinate')
        self.progress.pack()
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
        self.mblbox = Entry(self.root)
        self.pwdbox = Entry(self.root, show='*')

        self.x1 = tk.Label(self.root, text='mobile')
        self.x1.pack(side='top')
        self.mblbox.pack(side='top')

        self.x2 = tk.Label(self.root, text='password')
        self.x2.pack(side='top')

        self.pwdbox.pack(side='top')
        self.pwdbox.bind('<Return>', self.onpwdentry)

        self.x3 = Button(self.root, command=self.onokclick, text='Login')
        self.x3.pack(side='top')

    def init_window(self):
        self.root.geometry("200x150")
        self.root.resizable(height=None, width=None)
        self.root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
        self.root.title('Alaa studio app')

    def add_menu(self):
        self.menubar = tk.Menu(self.root)
        self.add_voice("Axis", self.axis)
        # self.add_voice("Convert", self.load_login)
        # self.add_voice("Convert", self.convert)
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
    # while os.stat('log.txt').st_size > 300:
    #     print(os.stat('log.txt').st_size)
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
