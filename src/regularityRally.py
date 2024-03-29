#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time
import subprocess
import pygame
import platform

from raceTimer import RaceTimer


class RegularityRally(RaceTimer):
    COUNTDOWN_TEMPLATE = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    SOUND_DELAY = 0.1

    def __init__(self):
        super().__init__()

        # Initialization of specific attributes.
        # Current folder
        self.folder_src = os.path.dirname(__file__)
        self.folder_main = os.path.dirname(self.folder_src)
        self.folder_support = os.path.join(self.folder_main, 'supportFiles')

        # Regularity config.
        self.config = {}
        self.mark_count = 0
        self.mark_stamps = []
        self.mark_labels = []
        self.mark_numbers = []

        # Set time.
        self.cur_set_time = None
        self.cur_set_time_decoded = None

        # Countdown.
        self.curlap_countdown_seconds = None
        self.curlap_countdown_text = None  # TODO: Check if needed
        self.cur_countdown_num = 0
        self.beep_done = False
        self.sound_delay = 0

        # Speak engine.
        self.countdown_checks = self.COUNTDOWN_TEMPLATE
        self.os = platform.system()

        # Beep engine.
        pygame.init()
        self.beep_object = pygame.mixer.Sound(os.path.join(self.folder_support, 'beep_outtake.wav'))

    def reg_update(self):
        # Perform timer update.
        self.update()

        # If confirmation lap, get countdown seconds.
        if self.state == 4:
            self.curlap_countdown_seconds = self.cur_set_time - self.curlap_seconds

            # Process countdown reading
            # Check if last countdown was already read.
            if self.cur_countdown_num is not None:
                # Check if countdown mark is reached and say it.
                if self.curlap_countdown_seconds <= self.cur_countdown_num + self.SOUND_DELAY:
                    self.espeak_say(self.cur_countdown_num)

                    # Check if countdown list is not empty and pop next item. Else apply None.
                    if self.countdown_checks:
                        self.cur_countdown_num = self.countdown_checks.pop(0)
                    else:
                        self.cur_countdown_num = None
            elif not self.beep_done and self.curlap_countdown_seconds <= 0:
                # If last mark was read, check for beep on time 0.
                self.beep_object.play()
                self.beep_done = True

            # Process marks reading.
            if len(self.mark_labels) > self.mark_count:
                if self.curlap_countdown_seconds <= self.mark_numbers[self.mark_count]:
                    self.espeak_say(self.mark_labels[self.mark_count])
                    self.mark_count += 1

    # Start new lap.
    def reg_new_lap(self, *args):
        # Save last state.
        last_state = self.state

        # Run basic new_lap method.
        self.new_lap()

        # Increment state count.
        self.state_count += 1

        # Get next lap state.
        if self.config is not None:
            # If config is loaded AND number of laps is greater than number of configured laps > get state from config.
            if self.state_count < len(self.config['states']):
                self.state = self.config['states'][self.state_count]
            else:
                # Else > Fast lap.
                self.state = 1

        else:
            if len(args):
                # If no config is loaded, get state from optional argument.
                self.state = args[0]
            else:
                # If nothing is given, start normal lap.
                self.state = 1

        # Update set time if applicable.
        if last_state == 3:
            self.cur_set_time = self.lap_times[-1]
            self.cur_set_time_decoded = self.lap_times_decoded[-1]

            # Also set calculate countdown times for marks.
            for ma_id, ma in enumerate(self.config['marks']):
                if len(self.mark_stamps) > ma_id:
                    self.config['marks'][ma] = self.time_stamps[-1] - self.mark_stamps[ma_id]
                else:
                    break

        # Reset countdown template at start of confirmation lap.
        if self.state == 4:
            self.countdown_checks = self.COUNTDOWN_TEMPLATE.copy()
            self.cur_countdown_num = self.countdown_checks.pop(0)
            self.beep_done = False
            if self.config['marks']:
                self.mark_numbers = list(self.config['marks'].values())

        # Reset mark count.
        self.mark_count = 0
        if self.state == 3:
            self.mark_stamps = []

    def espeak_say(self, text):
        if self.os == 'Windows':
            subprocess.Popen('{} {}'.format(self.config['misc']['espeakpath'],
                                            text))
        else:
            # TODO: Fix espeak for linux.
            pass
            # subprocess.Popen('espeak {}'.format(text))

    # Get the time stamp of a mark for state 3 (set lap).
    def mark_reached(self):
        if self.state == 3:
            self.mark_stamps.append(time.time())
            self.mark_count += 1

    # Reset the timer to the currently loaded configuration.
    def reset_config(self):
        self.state = 0
        self.state_count = -1
        self.time_stamps = []
        self.lap_times = []
        self.cur_set_time = None
        self.cur_set_time_decoded = None

    # Read a config from a config file.
    def read_config(self, config_file_path):
        # TODO: Except wrong format.

        # Select and open a configuration.
        with open(config_file_path) as config_file:
            config_text = config_file.readlines()

        # Re-Init config attribute.
        self.config = {'states': [],
                       'marks': {},
                       'misc': {},
                       }

        # Read basic state config.
        for k in config_text[0].strip():
            self.config['states'].append(int(k))

        # Read advanced config sections.
        section = ''
        for li in config_text:
            line = li.strip()
            # New section.
            if line.startswith('['):
                section = line[1:-1]

            # New Key-Value pair.
            elif '=' in line:
                line_split = line.split('=')

                if section in self.config:
                    self.config[section][line_split[0].strip()] = line_split[1].strip()

        if self.config['marks']:
            self.mark_labels = list(self.config['marks'].keys())

        if 'sound_delay' in self.config['misc']:
            self.sound_delay = float(self.config['misc']['sound_delay'])
