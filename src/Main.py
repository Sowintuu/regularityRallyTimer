#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import keyboard
import time

from raceTimer import RaceTimer


rt = RaceTimer()

while True:
    if keyboard.is_pressed('1'):
        print('Debug update.')
        rt.debug_update()
        time.sleep(0.15)

    elif keyboard.is_pressed('2'):
        print('Debug new lap.')
        rt.debug_new_lap()
        time.sleep(0.15)

# rt.read_config(r'..\config\GLP_norm.cfg')
