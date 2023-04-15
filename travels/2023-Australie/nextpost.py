"""
Next Post
"""


import sys
import os
import re
import tkinter as tk
import time
import configparser
import glob
import locale
import subprocess
import shutil

from datetime import datetime, timedelta
from tkinter import messagebox

import clipboard
import customtkinter
from pywinauto.application import Application
from pywinauto.timings import Timings
from pywinauto.keyboard import send_keys
from pywinauto import mouse

import addimg


class Options:
    def __init__(self):
        self.step = False


# -- Commands ----------------------------------------------------------------


MTPDRIVE = r"C:\Program Files\MTPdrive\MTPdrive.exe"
RECOMP = r'e:\Gilles\.portable\jpeg-archive\jpeg-recompress.exe %s %s'
FFMPEG = 'ffmpeg -i %s %s'

PATH = r'z:\DCIM\Camera\*.jpg'
PATH_SRC = r'z:\DCIM\Camera'
PATH_DST = r'D:\Gilles\github.io\travels\2023-Australie\photos'
PATH_SOUNDS = r'z:\Music\URecorder'
TEMP = r'c:\volatil'
INDEXMD = r"D:\Gilles\github.io\travels\2023-Australie\part1\index.md"


def connect_MTP_drive():
    print('on_transfer_photos')
    # backend = uia|win32
    t0 = time.time()
    app = Application(backend="uia").start(MTPDRIVE)
    win = app.window(title_re='MTPdrive', found_index=0)
    win.set_focus()
    send_keys('%m') # Mount z:

    while True:
        try:
            app = Application().connect(title=r"MTPdrive", found_index=0)
            win = app.window(title_re='MTPdrive', found_index=0)
            time.sleep(1)
            win.set_focus()
            send_keys('%{F4}')
        except:
            break

    os.system(r"dir z:\DCIM")  # necessary to force MTP connection
    os.system(r"dir z:\Music")  # necessary to force MTP connection
    time.sleep(1)
    print(time.time() - t0)


def latest_date(path_dst):
    files = (os.path.join(path_dst, fn) for fn in os.listdir(path_dst))
    latest = max(files, key=lambda fn: os.path.getmtime(fn))
    return os.path.getmtime(latest)


def is_same_date(t1, t2):
    """
    Check if the two provided timestamps represents the same date
    """
    return datetime.fromtimestamp(t1).date() == datetime.fromtimestamp(t2).date()


def list_of_photos():
    mtime = datetime.now().timestamp()
    dirs = glob.glob(PATH)
    list_of_files = [f for f in dirs if is_same_date(os.path.getmtime(os.path.join(PATH, f)), mtime)]
    print(list_of_files)
    return list_of_files


def medias_in_source(path_src, path_sounds):
    """
    Return the list of all medias in source with full path
    """
    files = os.listdir(path_src)

    photos = [os.path.join(path_src, fn) for fn in files if os.path.splitext(fn)[1] == '.jpg']
    movies = [os.path.join(path_src, fn) for fn in files if os.path.splitext(fn)[1] == '.mp4']
    sounds = [os.path.join(path_sounds, fn) for fn in os.listdir(path_sounds)]

    return photos, movies, sounds


def today_medias(path_src, path_sounds, path_dst):
    """
    Return the list of recent medias with full path
    """
    photos, movies, sounds = medias_in_source(path_src, path_sounds)
    latest_in_dest = latest_date(path_dst)

    photos = [fn for fn in photos if os.path.getmtime(fn) > latest_in_dest]
    movies = [fn for fn in movies if os.path.getmtime(fn) > latest_in_dest]
    sounds = [fn for fn in sounds if os.path.getmtime(fn) > latest_in_dest]

    return photos, movies, sounds


def transfer_medias(tkapp):
    connect_MTP_drive()

    photos, movies, sounds = today_medias(PATH_SRC, PATH_SOUNDS, PATH_DST)
    for photo in photos:
        print(photo)
        shutil.copy(photo, TEMP)
    for movie in movies:
        print(movie)
        shutil.copy(movie, TEMP)
    for sound in sounds:
        print(sound)
        shutil.copy(sound, TEMP)

    tkapp.statusbar_blink(5, 'Disconnect phone', lambda: recompress(photos, movies, sounds))


def recompress(photos, movies, sounds):
    for index, photo in enumerate(photos, 1):
        print(index, '/', len(photos), ':', photo)
        basename = os.path.basename(photo)
        os.system(RECOMP % (os.path.join(TEMP, basename), os.path.join(PATH_DST, basename)))
        os.remove(os.path.join(TEMP, basename))
        # break

    for index, movie in enumerate(movies, 1):
        print(index, '/', len(movies), ':', movie)
        basename = os.path.basename(movie)
        os.system(FFMPEG % (os.path.join(TEMP, basename), os.path.join(PATH_DST, basename)))
        os.remove(os.path.join(TEMP, basename))

    for index, sound in enumerate(sounds, 1):
        print(index, '/', len(sounds), ':', sound)
        basename = os.path.basename(sound)
        shutil.copy(os.path.join(TEMP, basename), PATH_DST)
        os.remove(os.path.join(TEMP, basename))

    print('Transfer done')


def update_stats():
    os.startfile(r"D:\Gilles\github.io\travels\2023-Australie\2023-Australie.ods")


POST = """\
[%s]

### J%d - %s - %s - %d km (%d km)

.

![](tmp.jpg)
______
"""


def latest_post_data(indexmd):
    """
    Parse latest post and return date, day and total kilometers.
    """
    with open(indexmd) as f:
        lines = f.readlines()
        slines = ''.join(lines)

    posts = re.findall(r'\[\d\d\d\d/\d\d/\d\d\]\n\n###.*', slines)
    last = posts[-1]
    print(last)
    match = re.match(r'\[(\d\d\d\d/\d\d/\d\d)\]\n\n### J(\d+).*\((\d+) km\)', last)
    date, day, total = match.group(1, 2, 3)
    day = int(day)
    total = int(total)
    return lines, date, day, total


def add_to_diary(place, km):
    lines, date, day, total = latest_post_data(INDEXMD)
    print(date, day, total)

    date_object = datetime.strptime(date, '%Y/%m/%d')
    print(date_object)
    date_object = date_object + timedelta(days=1)
    print(date_object)
    next_date = date_object.strftime('%Y/%m/%d')
    next_day = date_object.strftime('%e %B')
    print(next_date)
    print(next_day)

    post = POST % (next_date, day + 1, next_day, place, km, total + km)
    print(post)
    lines += post.lstrip()

    with open(INDEXMD, 'wt') as f:
        f.writelines(lines)


def create_new_post(place_km_str):
    print('>', place_km_str)
    place, km = place_km_str.split(',')
    km = int(km)
    add_to_diary(place, km)
    select_pictures1()


def select_pictures1():
    os.system(r'galerie --gallery part1\index-full.html --diary true --source photos --git true --dates 20230313-20230615')
    os.startfile(r"D:\Gilles\github.io\travels\2023-Australie\part1\index-full.html")


def select_pictures2():
    print('select_pictures2')
    addimg.main()
    os.system('galerie --gallery part1 --diary true --git true --google true')
    os.startfile(r"D:\Gilles\github.io\travels\2023-Australie\part1\index.html")


def edit_text():
    os.startfile(r"D:\Gilles\github.io\travels\2023-Australie\part1\index.md")


def review_post():
    os.system('galerie --gallery part1 --diary true --git true --google true')
    os.startfile(r"D:\Gilles\github.io\travels\2023-Australie\part1\index.html")


def commit():
    cmd = 'git ls-files --others --exclude-standard part1\thumbnails'
    output = subprocess.check_output(cmd.split())
    output = output.decode().splitlines()
    output = [fn for fn in output if 'post-IMG_' in fn]
    print(output)
    os.system('git add ' + ' '.join(output))

    _, _, day, _ = latest_post_data(INDEXMD)
    os.system(f'git commit -m "Add day {day}."')


def quit_command(tkapp):
    save_window_position(tkapp)
    exit(0)


def sync(tkapp, path_src, path_sounds, path_dst):
    connect_MTP_drive()
    photos, movies, sounds = medias_in_source(path_src, path_sounds)
    files_src = photos + movies + sounds
    files_dst = [os.path.join(path_dst, fn) for fn in os.listdir(path_dst)]
    basenames_dst = list(map(os.path.basename, files_dst))
    print(basenames_dst)
    for file in files_src:
        if os.path.basename(file) not in basenames_dst:
            shutil.copy(file, TEMP)
            print(file)
    messagebox.showinfo(title='Sync', message=f'Clean {TEMP} and keep only relevant medias.')


# -- Configuration file ------------------------------------------------------


def load_config():
    """
    Ensure config file exists and has required sections.
    Return configparser.
    """
    config_filename = 'nextpost.ini'
    config = configparser.ConfigParser(delimiters='=')

    if not os.path.exists(config_filename):
        with open(config_filename, 'wt') as configfile:
            config.write(configfile)

    config.read(config_filename)
    if not config.has_section('Window'):
        config.add_section('Window')
    if not config.has_section('Collections'):
        config.add_section('Collections')

    return config


def save_config(config):
    config_filename = 'nextpost.ini'
    with open(config_filename, 'wt') as configfile:
        config.write(configfile)


def save_window_position(app):
    config = load_config()
    config.set('Window', 'Position', f'{app.winfo_x()},{app.winfo_y()}')
    save_config(config)


def load_window_position(app):
    config = load_config()

    position = config.get('Window', 'Position', fallback=None)
    if position is None:
        return
    else:
        x, y = [int(_) for _ in position.split(',')]
        app.geometry(f"300x550+{x}+{y}")


# -- GUI root ----------------------------------------------------------------


DX = 20
DY = 30
DCB = 20


class App(customtkinter.CTk):
    def __init__(self, parent=None):
        customtkinter.CTk.__init__(self, parent)
        self.wheel_mode = 'wheel_digit'
        self.current_digit = 1
        self.current_color = 0

    def initialize(self):
        load_window_position(self)
        self.resizable(False, False)
        self.title('Next post')
        yplace = 10

        # Transfer photos
        self.checkbox1 = customtkinter.CTkCheckBox(
            master=self,
            text="Tranfer photos (connect phone first)",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox1.place(x=DX, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_transfer_photos2
        )
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Update stats
        self.checkbox2 = customtkinter.CTkCheckBox(
            master=self,
            text="Update stats",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox2.place(x=DX, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_update_stats
        )
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Create new post
        self.checkbox3 = customtkinter.CTkCheckBox(
            master=self,
            text="Create new post",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox3.place(x=DX, y=yplace)
        yplace += DY
        self.entry = customtkinter.CTkEntry(
            master=self,
            placeholder_text="place, km",
            width=210,
            height=25,
        )
        self.entry.place(x=DX+30, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_create_new_post
        )
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Select pictures
        self.checkbox4 = customtkinter.CTkCheckBox(
            master=self,
            text="Select pictures (copy to clipboard)",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox4.place(x=DX, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_select_pictures2
        )
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Edit text
        self.checkbox5 = customtkinter.CTkCheckBox(
            master=self,
            text="Edit text (Recharge)",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox5.place(x=DX, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_edit_text
        )
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Review post
        self.checkbox6 = customtkinter.CTkCheckBox(
            master=self,
            text="Review post",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox6.place(x=DX, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_review_post)
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Commit
        self.checkbox7 = customtkinter.CTkCheckBox(
            master=self,
            text="Commit",
            checkbox_width=DCB,
            checkbox_height=DCB,
            state=tk.DISABLED,
            text_color_disabled='black'
        )
        self.checkbox7.place(x=DX, y=yplace)
        yplace += DY
        button = customtkinter.CTkButton(
            master=self,
            text="Go",
            command=self.on_commit)
        button.place(x=DX+30, y=yplace)
        yplace += DY

        # Sync
        yplace += 30
        button = customtkinter.CTkButton(
            master=self,
            text="Sync",
            command=self.on_sync)
        button.place(x=DX+30, y=yplace)
        yplace += DY

        self.statusbar = tk.Label(self, relief=tk.SUNKEN, anchor="w")
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.protocol("WM_DELETE_WINDOW", lambda: quit_command(self))

    def on_transfer_photos1(self):
        connect_MTP_drive()

    def on_transfer_photos2(self):
        self.checkbox1.select()
        transfer_medias(self)

    def on_update_stats(self):
        self.checkbox2.select()
        update_stats()

    def on_create_new_post(self):
        self.checkbox3.select()
        create_new_post(self.entry.get())

    def on_select_pictures1(self):
        select_pictures1()

    def on_select_pictures2(self):
        self.checkbox4.select()
        select_pictures2()

    def on_edit_text(self):
        self.checkbox5.select()
        edit_text()

    def on_review_post(self):
        self.checkbox6.select()
        review_post()

    def on_commit(self):
        self.checkbox7.select()
        commit()

    def on_sync(self):
         sync(self, PATH_SRC, PATH_SOUNDS, PATH_DST)

    def on_unmap(self, event):
        return
        self.win.minimize()

    def on_map(self, event):
        return
        self.win.maximize()

    def statusbar_blink(self, count, msg, after_blink=None):
        self.count = count * 2 - 1
        self.msg = msg
        self.after_blink = after_blink
        self.statusbar_blink_rec()

    def statusbar_blink_rec(self):
        print(f'{self.count=}')
        if self.count % 2 == 0:
            self.statusbar.configure(text='')
        else:
            self.statusbar.configure(font=("Helvetica", 10, "bold"))
            self.statusbar.configure(fg="Red")
            self.statusbar.configure(text=self.msg)
        if self.count == 0:
            if self.after_blink:
                self.after_blink()
        else:
            self.count -= 1
            self.after(600, self.statusbar_blink_rec)


# -- Main --------------------------------------------------------------------


def main():
    locale.setlocale(locale.LC_TIME, 'fr_FR')

    customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
    customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    Timings.fast()
    Timings.window_find_timeout = 1

    app = App()
    app.initialize()
    app.mainloop()


if __name__ == '__main__':
    main()
