#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import pathlib
from tkinter import Tk, Menu, Label, Text, filedialog
from tkinter.ttk import Progressbar, Style
import tkinter.font as tk_font

import pyttsx3

from regularityRally import RegularityRally


class RegularityRallyGUI(RegularityRally):
    STATES = {-1: 'Select configuration',
              0: 'Ready',
              1: 'Fast Lap',
              2: 'Untimed Lap',
              3: 'Set Lap',
              4: 'Confirmation Lap'}

    def __init__(self):
        super().__init__()

        # Data attribute initialization.
        self.root_dir = pathlib.Path(__file__).parent.parent.absolute()
        self.config_dir = os.path.join(self.root_dir, 'config')

        # Overwrite initial state. Config read is mandatory here.
        self.state = -1

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
        self.t_laps = None
        self.bar_progress = None
        self.style_progress = None

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
        file_menu.add_command(label='Exit', command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        extras_menu = Menu(menu_bar, tearoff=0)
        extras_menu.add_command(label='Set new start time', command=None)
        extras_menu.add_command(label='Manage Config Files', command=None)
        extras_menu.add_command(label='Options', command=None)
        menu_bar.add_cascade(label="Extras", menu=extras_menu)

        self.master.config(menu=menu_bar)

        # Init Widgets.
        # TODO: Resize and anchor Labels.
        # Information row.
        row_count = 0
        self.l_state = Label(self.master, text='Select Configuration', font=self.font)
        self.l_state.grid(row=row_count, column=0)
        self.l_countdown = Label(self.master, text='', font=self.font)
        self.l_countdown.grid(row=row_count, column=1)
        self.t_laps = Text(self.master, width=20, font=("Consolas", 32))
        self.t_laps.grid(row=row_count, column=2, rowspan=3)
        self.master.grid_rowconfigure(row_count, weight=1)

        # Labels row.
        row_count += 1
        self.l_cur_lap = Label(self.master, text='Current Lap', anchor='w', font=self.font)
        self.l_cur_lap.grid(row=row_count, column=0)
        self.l_set_lap = Label(self.master, text='Current Set Lap', anchor='w', font=self.font)
        self.l_set_lap.grid(row=row_count, column=1)
        self.master.grid_rowconfigure(row_count, weight=1)

        # Time display row.
        row_count += 1
        self.l_cur_lap_disp = Label(self.master, text='__:__:__', anchor='w', font=self.font)
        self.l_cur_lap_disp.grid(row=row_count, column=0)
        self.l_set_lap_disp = Label(self.master, text='__:__:__', anchor='w', font=self.font)
        self.l_set_lap_disp.grid(row=row_count, column=1)
        self.master.grid_rowconfigure(row_count, weight=1)

        # Progressbar and countdown row.
        row_count += 1
        # Create the progressbar style to be labeled.
        self.style_progress = Style(self.master)
        self.style_progress.layout("LabeledProgressbar",
                                   [('LabeledProgressbar.trough',
                                     {'children': [('LabeledProgressbar.pbar',
                                                    {'side': 'left', 'sticky': 'ns'}),
                                                   ("LabeledProgressbar.label",  # label inside the bar
                                                    {"sticky": ""})],
                                      'sticky': 'nswe'})])
        self.bar_progress = Progressbar(self.master, orient='horizontal', length=1000, mode='determinate',
                                        style="LabeledProgressbar")
        self.bar_progress.grid(row=row_count, column=0, columnspan=3)

        # Column configuration.
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        # Define Binds.
        self.master.bind('1', self.one_cb)

        # Start master mainloop.
        self.master.after(10, self.gui_update)
        self.master.mainloop()

    def gui_update(self):
        # Calculate time delta of current lap.
        if self.state > 0:

            # Call regularity update.
            self.reg_update()

            # Update current lap time display.
            self.l_cur_lap_disp['text'] = '{:02}:{:02}:{:02}.{:03}'.format(self.curlap_decoded[0],
                                                                           self.curlap_decoded[1],
                                                                           self.curlap_decoded[2],
                                                                           self.curlap_decoded[3])

            # Update countdown display, if confirmation lap.
            if self.state == 4:
                self.bar_progress['value'] = self.curlap_countdown_seconds
                self.style_progress.configure("LabeledProgressbar", text='{:.2f}'.format(self.curlap_countdown_seconds))
                self.bar_progress.update()
            else:
                self.bar_progress['value'] = 0
                self.style_progress.configure("LabeledProgressbar", text='')

        # Schedule next call.
        self.master.after(10, self.gui_update)

    # Method called, when new race should be created.
    def new_cb(self):
        # Select and open a configuration.
        conf_file = open(filedialog.askopenfilename(initialdir=self.config_dir,
                                                    title='Select file',
                                                    filetypes=(('Configuration', "*.cfg"), ("all files", "*.*"))))

        # Read configuration.
        self.read_config(conf_file.name)

        # Write state.
        self.state = 0
        self.l_state['text'] = 'Ready'

    # Method for new lap.
    # Only update displays here. Set data in regularityRally.reg_new_lap()
    def one_cb(self, _):
        if self.state == -1:
            self.new_cb()
        else:
            # Store last state.
            last_state = self.state

            # Perform new lap method.
            self.reg_new_lap()

            # Change label.
            self.l_state['text'] = self.STATES[self.state]

            # Update lap times text field.
            self.t_laps.delete(1.0, 'end')
            for lt_id, lt in enumerate(self.lap_times_decoded):
                # Get text char from config. If id out of config, set 'F.
                if lt_id < len(self.config['states']):
                    state_char = self.STATES[self.config['states'][lt_id]][0]
                else:
                    state_char = 'F'

                # Set char for each lap.
                self.t_laps.insert('end', '  {}: {:02}:{:02}:{:02}.{:03} {}\n'.format(lt_id + 1,
                                                                                      lt[0], lt[1], lt[2], lt[3],
                                                                                      state_char))

            # Update GUI items related to set lap.
            if self.cur_set_time is not None:
                # Update shown set time.
                self.l_set_lap_disp['text'] = '{:02}:{:02}:{:02}.{:03}'.format(self.cur_set_time_decoded[0],
                                                                               self.cur_set_time_decoded[1],
                                                                               self.cur_set_time_decoded[2],
                                                                               self.cur_set_time_decoded[3])

                # Update progressbar maximum to set lap time to show countdown.
                self.bar_progress['maximum'] = self.cur_set_time

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
