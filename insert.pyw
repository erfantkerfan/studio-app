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


Insert('erfan ')
