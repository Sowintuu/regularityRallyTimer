import time
import os
import pathlib


class RaceTimer(object):

    def __init__(self):
        # Data attribute initialization.
        # Directories.
        self.root_dir = pathlib.Path(__file__).parent.parent.absolute()
        self.config_dir = os.path.join(self.root_dir, 'config')

        # Configuration.
        self.cur_config = None
        self.cur_config_file = None

        # Lap state.
        # 0: No config
        # 1: Ready
        # 2: Untimed lap
        # 3: Set lap
        # 4: Confirmation lap
        # 5: Sprint lap
        self.state = 0
        self.state_count = -1   # Initialised with -1 to be set to 0 on start.

        # Coordinates.
        self.finish_line_coordinates = [None] * 2

        # Times.
        self.time_stamps = []
        self.lap_times = []
        self.set_time_current = None

        self.curlap_seconds = None
        self.curlap_string = None
        self.curlap_countdown_seconds = None
        self.curlap_countdown_text = None

    # Method to be executed continuously.
    def mainloop_task(self):
        # Get current time stamp.
        current_time_stamp = time.time()

        # Get current lap seconds.
        if self.state > 1:
            self.curlap_seconds = current_time_stamp - self.time_stamps[-1]

        # If confirmation lap, get countdown seconds.
        if self.state == 4:
            self.curlap_countdown_seconds = self.set_time_current - current_time_stamp

    # Method to start a new lap.
    # Stops time for previous lap and sets state.
    def new_lap(self, lap_type):

        # If no config loaded, return False.
        if not self.state:
            return False

        # Append current time as stamp.
        self.time_stamps.append(time.time())

        # Increment state count.
        self.state_count += 1

        # Get lap time if not first lap. $
        if len(self.time_stamps) > 1:
            self.lap_times.append(self.time_stamps[-1] - self.time_stamps[-2])

        # If last lap was set lap, save new set time
        if self.state == 3:
            self.set_time_current = self.lap_times[-1]

        # Get current lap state.
        self.state = self.cur_config[self.state_count]

        return True

    # Reset the timer to the currently loaded configuration.
    def reset_config(self):
        self.state = 1
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
        self.cur_config = []
        # TODO: Except non numeric char.
        for k in config_text[0]:
            self.cur_config.append(int(k) + 2)

        # Write state.
        self.state = 1


