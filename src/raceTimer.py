#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import os
import pathlib

from util import decode_seconds


# TODO: Add autosave file


class RaceTimer(object):

    def __init__(self):
        # Data attribute initialization.
        # Directories.
        self.root_dir = pathlib.Path(__file__).parent.parent.absolute()
        self.config_dir = os.path.join(self.root_dir, 'config')

        # Configuration.
        self.config = None
        self.config_file = None

        # Lap state.
        # 0: Ready
        # 1: Normal lap (sprint)
        # 2: Untimed lap
        # 3: Set lap
        # 4: Confirmation lap
        self.state = 0
        self.state_count = -1  # Initialised with -1 to be set to 0 on start.

        # Coordinates.
        self.finish_line_coordinates = [None] * 2

        # Times.
        self.time_stamps = []
        self.lap_times = []
        self.lap_times_decoded = []

        self.curlap_seconds = None
        self.curlap_decoded = [0.0] * 3
        self.curlap_string = None

        self.cur_time_stamp = None

        # Init finished.
        print('Initialisation finished.')

    # Method to be executed continuously.
    def update(self):
        # Get current time stamp.
        self.cur_time_stamp = time.time()

        # Get current lap seconds.
        if self.state:
            self.curlap_seconds = self.cur_time_stamp - self.time_stamps[-1]
            self.curlap_decoded = decode_seconds(self.curlap_seconds)

    # Method to start a new lap.
    # Stops time for previous lap and sets state.
    def new_lap(self):

        # Append current time as stamp.
        # This must always be the first statement to keep the error low!
        self.time_stamps.append(time.time())

        # Get lap time if not first lap. $
        if len(self.time_stamps) > 1:
            # Get time in seconds.
            time_seconds = self.time_stamps[-1] - self.time_stamps[-2]

            # Add time in seconds and decoded to the related attributes.
            self.lap_times.append(time_seconds)
            self.lap_times_decoded.append(decode_seconds(time_seconds))

    # Update lap attributes and print current time.
    def debug_update(self):
        self.update()
        print('Time: {:02d}:{:02d}:{:02d}.{}'.format(int(self.curlap_decoded[0]),
                                                     int(self.curlap_decoded[1]),
                                                     int(self.curlap_decoded[2]),
                                                     int(self.curlap_decoded[3]))
              )

    def debug_new_lap(self):
        self.new_lap()
