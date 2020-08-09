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
        self.add_voice("Convert", self.convert)
        self.add_voice("Quit", self.quit_window)
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

        os.startfile(directory.replace('/', '\\'))
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        self.space.pack_forget()
        self.progress_bar.pack_forget()
        self.percent_text.pack_forget()
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
        return None

    """convert section"""

    def convert(self):
        self.file_name = filedialog.askopenfilename(filetypes=(("mp4 files", "*.mp4"), ("All files", "*.*")))
        regex = re.compile(r"C:\\Alaa\\Finish\\\d{3,4}\\HD_720p")
        if self.file_name == "":
            return None
        elif not regex.match(str(self.file_name).replace('/', '\\')):
            toaster = ToastNotifier()
            toaster.show_toast("Path Invalid",
                               r'select a file in C:\Alaa\Finish',
                               icon_path='alaa.ico',
                               duration=2,
                               threaded=True)
            return None

        # return None
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
        self.total_duration = float(reg.group(0)) if reg else helper.parse_seconds("00:15:00")
        modified_file_name_hq = os.path.join(directory_hq, os.path.basename(self.file_name))
        modified_file_name_240p = os.path.join(directory_240p, os.path.basename(self.file_name))
        self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        thread = threading.Thread(target=self.start_convert,
                                  args=(self.file_name, modified_file_name_hq, modified_file_name_240p))
        self.welcome_text.pack_forget()
        self.root.config(menu="")
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
            self.progress_hq['value'] = helper.parse_seconds(self.ffmpeg_time_hq) / self.total_duration * 100
            self.progress_240p['value'] = helper.parse_seconds(self.ffmpeg_time_240p) / self.total_duration * 100
            self.root.update()

        os.startfile(os.path.dirname(self.file_name).replace('/', '\\'))
        self.root.protocol("WM_DELETE_WINDOW", self.quit_window)
        self.space.pack_forget()
        self.title_hq.pack_forget()
        self.progress_hq.pack_forget()
        self.title_240p.pack_forget()
        self.progress_240p.pack_forget()
        self.config_menu()
        self.root.update()

        toaster = ToastNotifier()
        toaster.show_toast("Convert Finished",
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


if __name__ == '__main__':
    helper.setup_logging()
    panel = Main()
