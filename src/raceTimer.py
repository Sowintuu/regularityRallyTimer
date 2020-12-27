import time
import os
import pathlib
from math import floor

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
        self.set_time_current = None

        self.curlap_seconds = None
        self.curlap_decoded = [0.0] * 3
        self.curlap_string = None
        self.curlap_countdown_seconds = None
        self.curlap_countdown_text = None

    # Method to be executed continuously.
    def update(self):
        # Get current time stamp.
        current_time_stamp = time.time()

        # Get current lap seconds.
        if self.state:
            self.curlap_seconds = current_time_stamp - self.time_stamps[-1]
            self.curlap_decoded = decode_seconds(self.curlap_seconds)

        # If confirmation lap, get countdown seconds.
        if self.state == 4:
            self.curlap_countdown_seconds = self.set_time_current - current_time_stamp

    # Method to start a new lap.
    # Stops time for previous lap and sets state.
    def new_lap(self, *args):

        # Append current time as stamp.
        self.time_stamps.append(time.time())

        # Increment state count.
        self.state_count += 1

        # Get lap time if not first lap. $
        if len(self.time_stamps) > 1:
            # Get time in seconds.
            time_seconds = self.time_stamps[-1] - self.time_stamps[-2]

            # Add time in seconds and decoded to the related attributes.
            self.lap_times.append(time_seconds)
            self.lap_times_decoded.append(decode_seconds(time_seconds))

        # If last lap was set lap, save new set time
        if self.state == 3:
            self.set_time_current = self.lap_times[-1]

        # Get next lap state.
        if self.config is not None:
            # If config is loaded, get state from config.
            self.state = self.config[self.state_count]
        else:
            if len(args):
                # If no config is loaded, get state from optional argument.
                self.state = args[0]
            else:
                # If nothing is given, start normal lap.
                self.state = 1

    # Reset the timer to the currently loaded configuration.
    def reset_config(self):
        self.state = 0
        self.state_count = -1
        self.time_stamps = []
        self.lap_times = []
        self.set_time_current = None

    # Read a config from the config file.
    def read_config(self, config_file_path):
        # Select and open a configuration.
        with open(config_file_path) as config_file:
            config_text = config_file.readlines()

        # Read configuration.
        self.config = []
        # TODO: Except non numeric char.
        for k in config_text[0]:
            self.config.append(int(k) + 2)

    # Update lap attributes and print current time.
    def debug_update(self):
        self.update()
        print('Time: {:02d}:{:02d}:{}'.format(self.curlap_decoded[0],
                                              self.curlap_decoded[1],
                                              self.curlap_decoded[2]))

    def debug_new_lap(self):
        self.new_lap()
