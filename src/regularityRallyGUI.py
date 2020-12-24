import datetime
import os
import pathlib
# import time
from tkinter import Tk, Menu, Label, filedialog
import tkinter.font as tk_font

import pyttsx3


class RegularityRally(object):

    STATES = {0 : 'Select configuration',
              1 : 'Ready',
              2 : 'Untimed Lap',
              3 : 'Set Lap',
              4 : 'Confirmation Lap'}

    def __init__(self):
        # Data attribute initialization.
        self.root_dir = pathlib.Path(__file__).parent.parent.absolute()
        self.config_dir = os.path.join(self.root_dir, 'config')
        self.cur_config = None
        self.cur_config_file = None
        self.state = 0
        self.state_count = 0
        # State definition
        # 0: No config
        # 1: Ready
        # 2: Untimed lap
        # 3: Set lap
        # 4: Confirmation lap

        # GUI attribute initialization.
        self.master = None
        self.font = None
        self.w = None
        self.h = None

        self.l_state = None
        self.l_countdown = None
        self.l_cur_lap = None
        self.l_cur_lap_disp = None
        self.l_set_lap = None
        self.l_set_lap_disp = None

        # Get start time.
        self.time_stamps = []

        # Init speak engine.
        self.speak_engine = pyttsx3.init()

        # Window initialization.
        self.init_window()

    def init_window(self):
        # Create main window
        self.master = Tk()
        self.master.title('Regularity Rally Timer')

        # Resize window.
        self.master.state('zoomed')
        self.w = self.master.winfo_screenwidth()
        self.h = self.master.winfo_screenheight()

        # Init font variable.
        self.font = tk_font.Font(family="Helvetica", size=36, weight="bold")

        # Create menu
        menu_bar = Menu(self.master)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New', command=self.new_cb)
        file_menu.add_command(label='Manage Config Files')
        file_menu.add_command(label='Exit', command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.master.config(menu=menu_bar)

        # Init Widgets.
        # TODO: Resize and anchor Labels.
        row_count = 0
        self.l_state = Label(self.master, text='Select Configuration', font=self.font)
        self.l_state.grid(row=row_count, column=0)
        self.l_countdown = Label(self.master, text='', font=self.font)
        self.l_countdown.grid(row=row_count, column=1)
        self.master.grid_rowconfigure(row_count, weight=1)

        row_count += 1
        self.l_cur_lap = Label(self.master, text='Current Lap', anchor='w', font=self.font)
        self.l_cur_lap.grid(row=row_count, column=0)
        self.l_set_lap = Label(self.master, text='Current Set Lap', anchor='w', font=self.font)
        self.l_set_lap.grid(row=row_count, column=1)
        self.master.grid_rowconfigure(row_count, weight=1)

        row_count += 1
        self.l_cur_lap_disp = Label(self.master, text='__:__:__', anchor='w', font=self.font)
        self.l_cur_lap_disp.grid(row=row_count, column=0)
        self.l_set_lap_disp = Label(self.master, text='__:__:__', anchor='w ', font=self.font)
        self.l_set_lap_disp.grid(row=row_count, column=1)
        self.master.grid_rowconfigure(row_count, weight=1)

        # Column configuration.
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        # Define Binds.
        self.master.bind('1', self.one_cb)

        # Start master mainloop.
        self.master.after(10, self.mainloop_task)
        self.master.mainloop()

    def mainloop_task(self):

        if self.state > 1:
            time_delta = datetime.datetime.now().replace(microsecond=0) - self.time_stamps[-1].replace(microsecond=0)
            self.l_cur_lap_disp['text'] = time_delta

        # TODO: Implement countdown.
        if self.state == 4:
            pass

        # Schedule next call.
        self.master.after(10, self.mainloop_task)

    def new_cb(self):
        # Select and open a configuration.
        with open(filedialog.askopenfilename(initialdir=self.config_dir,
                                             title='Select file',
                                             filetypes=(('Configuration', "*.cfg"), ("all files", "*.*")))) \
                as conf_file:
            conf_file_text = conf_file.readlines()

        # Read configuration.
        self.cur_config = []
        # TODO: Except non numeric char.
        for k in conf_file_text[0]:
            self.cur_config.append(int(k)+2)

        # Write state.
        self.state = 1
        self.l_state['text'] = 'Ready'

    def one_cb(self, _):
        if self.state == 0:
            self.new_cb()
        else:
            self.time_stamps.append(datetime.datetime.now())


            print(self.state)

            # 0: No config
            # 1: Ready
            if self.state == 1:
                self.state = self.cur_config[self.state_count]

            else:
                self.state_count += 1
                self.state = self.cur_config[self.state_count]
                self.l_state['text'] = self.STATES[self.state]

            # # 2: Untimed lap
            # elif self.state == 2:
            #     pass
            #
            # # 3: Set lap
            # elif self.state == 3:
            #     pass
            #
            # # 4: Confirmation lap
            # elif self.state == 4:
            #     pass

        # print('1 pressed')
        # self.speak_engine.say("5")
        # self.speak_engine.runAndWait()
        # time.sleep(1)
        # self.speak_engine.say("4")
        # self.speak_engine.runAndWait()
        # time.sleep(1)
        # self.speak_engine.say("3")
        # self.speak_engine.runAndWait()
        # time.sleep(1)
        # self.speak_engine.say("2")
        # self.speak_engine.runAndWait()
        # time.sleep(1)
        # self.speak_engine.say("1")
        # self.speak_engine.runAndWait()


if __name__ == '__main__':
    regRal = RegularityRally()
