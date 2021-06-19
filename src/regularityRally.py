#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from raceTimer import RaceTimer


class RegularityRally(RaceTimer):

    def __init__(self):
        super().__init__()

        # Initialization of specific attributes.
        # Regularity config.
        self.config = {}

        # Set time.
        self.cur_set_time = None
        self.cur_set_time_decoded = None

        # Countdown.
        self.curlap_countdown_seconds = None
        self.curlap_countdown_text = None

    def reg_update(self):
        # Perform timer update.
        self.update()

        # If confirmation lap, get countdown seconds.
        if self.state == 4:
            self.curlap_countdown_seconds = self.cur_set_time - self.curlap_seconds

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
                       'marks': {}}

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

            # TODO: Sort marks.

        pass
