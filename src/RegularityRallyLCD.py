#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import time
import keyboard
import configparser
from datetime import datetime, timedelta
from math import floor

from regularityRally import RegularityRally

# Try to import raspberry pi packages.
try:
    # noinspection PyUnresolvedReferences
    import RPi.GPIO as GPIO
    debug = False
except ImportError:
    # Else assume, it is called in windows and start debug mode.
    debug = True


class RegularityRallyLCD(RegularityRally):
    # Chars for state display.
    STATES = {-1: 'o',  # No config (should not appear).
              0: 'x',  # Ready
              1: '*',  # Sprint Lap
              2: 'U',  # Untimed Lap
              3: 'S',  # Set Lap
              4: 'C'}  # Confirmation Lap

    BUTTON_DEBOUNCE_TIME = 0.5  # s

    def __init__(self, no_button=False):
        super().__init__()

        # Init variables.
        self.display_string = ['--:--.-  --:--.-', '--.- -- - ------']

        self.no_button = no_button

        # Init time for debounce to a date in the past.
        self.time_last_press = datetime(2021, 1, 1, 0, 0, 0, 0)

        # Print placeholder if debug mode.
        if debug:
            print('{} - {}'.format(self.display_string[0], self.display_string[1]), end='')

        # Read config.
        self.read_config(os.path.join(self.config_dir, 'LCD.cfg'))
        self.state = 0

        # Read gpio config.
        self.gpio = {}
        self.read_gpio_cfg()

        # Init LCD config.
        self.lcd_init()

        # Run mainloop
        self.mainloop()

    def mainloop(self):
        while True:
            self.update_display_string()

            if not debug and not self.no_button:
                # TODO: Insert GPIO button detection.
                pass
            else:
                if debug:
                    self.print_display_debug()
                else:
                    self.print_display()
                if keyboard.is_pressed('1') and self.check_last_press():
                    self.cb_button_1()
                elif keyboard.is_pressed('2') and self.check_last_press():
                    self.cb_button_2()

    # Writes the display string for the LCD display.
    # Consists of two lines with exactly 16 chars. Format as below
    # xxxxxxxxxxxxxxxx
    # 00:00.0  00:00.0
    # 00.0 99 C BRIDGE
    # xxxxxxxxxxxxxxxx
    def update_display_string(self):

        # Init variables for state <=0 (No config or ready).
        lap_time_str = '--:--.-'
        ref_time_str = '--:--.-'
        countdown_str = '--.-'
        lap_count = 0
        lap_type_char = self.STATES[self.state]
        mark_str = '------'

        # Calculate time delta of current lap.
        if self.state > 0:

            # Call regularity update.
            self.reg_update()

            # Update current lap time display.
            lap_time_str = '{:02}:{:02}.{:01}'.format(self.curlap_decoded[1],
                                                      self.curlap_decoded[2],
                                                      floor(self.curlap_decoded[3] / 100))

            # Get lap count.
            lap_count = len(self.lap_times) + 1

            # Update countdown display, if confirmation lap.
            if self.state == 4:
                # Get countdown.
                countdown_str = '{:04.1f}'.format(self.curlap_countdown_seconds)

                # Get set time and use as ref time.
                # TODO: Show last time, if not confirmation lap.
                ref_time_str = '{:02}:{:02}.{:01}'.format(self.cur_set_time_decoded[1],
                                                          self.cur_set_time_decoded[2],
                                                          floor(self.cur_set_time_decoded[3] / 100))

            elif len(self.lap_times):
                # If not in confirmation lap. Show last lap as ref time.
                ref_time_str = '{:02}:{:02}.{:01}'.format(self.lap_times_decoded[-1][1],
                                                          self.lap_times_decoded[-1][2],
                                                          floor(self.lap_times_decoded[-1][3] / 100))

            # Get mark label.
            if self.state in [3, 4]:
                if self.mark_count < len(self.mark_labels):
                    mark_str = self.mark_labels[self.mark_count][0:6]
                else:
                    mark_str = 'FINISH'

        # Compose string.
        self.display_string = ['{}  {}'.format(lap_time_str, ref_time_str),
                               '{} {: 2} {} {}'.format(countdown_str, lap_count, lap_type_char, mark_str)]

        # Schedule next call.
        pass

    def print_display(self):
        self.lcd_send_byte(self.gpio['lcd_line_1'], GPIO.LOW)
        self.lcd_message(self.display_string[0])
        self.lcd_send_byte(self.gpio['lcd_line_2'], GPIO.LOW)
        self.lcd_message(self.display_string[1])

    def print_display_debug(self):
        print('\r{} - {}'.format(self.display_string[0], self.display_string[1]), end='')

    # Check if last press was within debounce time.
    # Return True and reset time, if not.
    def check_last_press(self):
        # Get current time.
        cur_time = datetime.now()

        # Calculate time delta.
        timedelta_pressed = cur_time - self.time_last_press

        # Check if time delta greater than debounce time.
        if timedelta_pressed > timedelta(seconds=self.BUTTON_DEBOUNCE_TIME):
            valid_press = True
            self.time_last_press = cur_time
        else:
            valid_press = False

        # Return result.
        return valid_press

    def cb_button_1(self):
        # Perform new lap method.
        self.reg_new_lap()

    def cb_button_2(self):
        # Execute superclass method.
        self.mark_reached()

    def read_gpio_cfg(self):
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(self.root_dir, 'supportFiles', 'GPIO.cfg'))

        for gp in cfg['Main']:
            try:
                self.gpio[gp] = cfg.getint('Main', gp)
            except ValueError:
                try:
                    self.gpio[gp] = cfg.getfloat('Main', gp)
                except ValueError:
                    self.gpio[gp] = cfg.get('Main', gp)

    def lcd_send_byte(self, bits, mode):
        # Set Pins to LOW
        GPIO.output(self.gpio['lcd_rs'], mode)
        GPIO.output(self.gpio['lcd_data4'], GPIO.LOW)
        GPIO.output(self.gpio['lcd_data5'], GPIO.LOW)
        GPIO.output(self.gpio['lcd_data6'], GPIO.LOW)
        GPIO.output(self.gpio['lcd_data7'], GPIO.LOW)
        if bits & 0x10 == 0x10:
            GPIO.output(self.gpio['lcd_data4'], GPIO.HIGH)
        if bits & 0x20 == 0x20:
            GPIO.output(self.gpio['lcd_data5'], GPIO.HIGH)
        if bits & 0x40 == 0x40:
            GPIO.output(self.gpio['lcd_data6'], GPIO.HIGH)
        if bits & 0x80 == 0x80:
            GPIO.output(self.gpio['lcd_data7'], GPIO.HIGH)
        time.sleep(self.gpio['e_delay'])
        GPIO.output(self.gpio['lcd_e'], GPIO.HIGH)
        time.sleep(self.gpio['e_pulse'])
        GPIO.output(self.gpio['lcd_e'], GPIO.LOW)
        time.sleep(self.gpio['e_delay'])
        GPIO.output(self.gpio['lcd_data4'], GPIO.LOW)
        GPIO.output(self.gpio['lcd_data5'], GPIO.LOW)
        GPIO.output(self.gpio['lcd_data6'], GPIO.LOW)
        GPIO.output(self.gpio['lcd_data7'], GPIO.LOW)
        if bits & 0x01 == 0x01:
            GPIO.output(self.gpio['lcd_data4'], GPIO.HIGH)
        if bits & 0x02 == 0x02:
            GPIO.output(self.gpio['lcd_data5'], GPIO.HIGH)
        if bits & 0x04 == 0x04:
            GPIO.output(self.gpio['lcd_data6'], GPIO.HIGH)
        if bits & 0x08 == 0x08:
            GPIO.output(self.gpio['lcd_data7'], GPIO.HIGH)
        time.sleep(self.gpio['e_delay'])
        GPIO.output(self.gpio['lcd_e'], GPIO.HIGH)
        time.sleep(self.gpio['e_pulse'])
        GPIO.output(self.gpio['lcd_e'], GPIO.LOW)
        time.sleep(self.gpio['e_delay'])

    def lcd_init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.gpio['lcd_e'], GPIO.OUT)
        GPIO.setup(self.gpio['lcd_rs'], GPIO.OUT)
        GPIO.setup(self.gpio['lcd_data4'], GPIO.OUT)
        GPIO.setup(self.gpio['lcd_data5'], GPIO.OUT)
        GPIO.setup(self.gpio['lcd_data6'], GPIO.OUT)
        GPIO.setup(self.gpio['lcd_data7'], GPIO.OUT)

        self.lcd_send_byte(0x33, GPIO.LOW)
        self.lcd_send_byte(0x32, GPIO.LOW)
        self.lcd_send_byte(0x28, GPIO.LOW)
        self.lcd_send_byte(0x0C, GPIO.LOW)
        self.lcd_send_byte(0x06, GPIO.LOW)
        self.lcd_send_byte(0x01, GPIO.LOW)

    def lcd_message(self, message):
        message = message.ljust(self.gpio['lcd_width'], " ")
        for i in range(self.gpio['lcd_width']):
            self.lcd_send_byte(ord(message[i]), GPIO.HIGH)


if __name__ == '__main__':
    regRal = RegularityRallyLCD(no_button=True)
