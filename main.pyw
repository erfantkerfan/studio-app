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
import helper


class Main(object):
    """load the main window"""

    def __init__(self):
        self.root = tk.Tk()
        self.add_menu()
        self.init_window()
        self.load_landing()
        self.root.mainloop()

    def load_landing(self):
        self.config_menu()
        self.welcome_text = tk.Label(self.root, text=os.linesep * 3 + 'سلام آلایی عزیز')
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
        # self.add_voice("Convert", self.load_login)
        # self.add_voice("Convert", convert.convert)
        self.add_voice("Quit", self.quit_window)
        self.config_menu()

    def add_voice(self, label, command):
        self.menubar.add_command(label=label, command=command)

    def config_menu(self):
        self.root.config(menu=self.menubar)

    def quit_window(self):
        self.root.destroy()
        os._exit(0)

    """ axis section """

    def axis(self):
        self.file_name = filedialog.askopenfilename(filetypes=(("mkv files", "*.mkv"), ("All files", "*.*")))
        if self.file_name == "":
            return None
        directory = os.path.join(os.path.dirname(self.file_name), 'mp4')
        if not os.path.exists(directory):
            os.makedirs(directory)
        modified_file_name = os.path.join(directory, os.path.basename(self.file_name).replace('mkv', 'mp4'))
        thread = threading.Thread(target=self.start_axis, args=(self.file_name, modified_file_name))
        self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        self.welcome_text.pack_forget()
        self.root.config(menu="")
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

        os.startfile(directory)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        self.percent_text.pack_forget()
        self.progress_bar.pack_forget()
        self.space.pack_forget()
        self.config_menu()
        self.root.update()

        toaster = ToastNotifier()
        toaster.show_toast("Axis Finished",
                           self.file_name,
                           icon_path='alaa.ico',
                           duration=10,
                           threaded=True)
        self.root.destroy()
        self.__init__()

    def start_axis(self, input, output):
        command = "ffmpeg -y -v quiet -stats -i \"" + str(
            input) + "\" -metadata title=\"@alaa_sanatisharif\" -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 \"" + output + "\""
        logging.critical('axis command: ' + command)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True, shell=True)
        for line in self.process.stdout:
            reg = re.search('\d\d:\d\d:\d\d', line)
            self.ffmpeg_time = reg.group(0) if reg else ''


if __name__ == '__main__':
    helper.setup_logging()
    panel = Main()
