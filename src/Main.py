#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import keyboard
import time
import sys

from raceTimer import RaceTimer

write = sys.stdout.write

rt = RaceTimer()

while True:
    if keyboard.is_pressed('1'):
        print('Debug update.')
        rt.debug_update()
        print('Time: 00:00:00.000')

    elif keyboard.is_pressed('2'):
        print('Debug new lap.')
        rt.debug_new_lap()

    if rt.state:
        rt.update()
        # del_count = 0
        # while del_count < 12:
        #     write('\b')
        #     write(' ')
        #     write('\b')

        print('{:02d}:{:02d}:{:02d}.{}'.format(int(rt.curlap_decoded[0]),
                                               int(rt.curlap_decoded[1]),
                                               int(rt.curlap_decoded[2]),
                                               int(rt.curlap_decoded[3]))
              , end='\r')

    time.sleep(0.15)

# rt.read_config(r'..\config\GLP_norm.cfg')
