# This script supports ABX testing using a USB relay like this one:
# https://numato.com/docs/4-channel-usb-relay-module/
# http://s3.amazonaws.com/s3.image.smart/download/101-70-118/20-018-910.rar

import curses
import random
import sys
import paramiko
import time

# pip install pylibftdi
# brew install libftdi
from pylibftdi import Driver
from pylibftdi import BitBangDevice

from ctypes.util import find_library

device_id = 'A90799W0' # TODO: get this from command-line

# TODO: get below from command-line
# Note - we wire each source to the relays on for one channel and off for the
# other so that whenever we switch, there's always a click (relay only clicks
# audibly when switching on, which would bias test).
sources = {
    'a': {
        'key': 'a',
        'name': 'Desktop',
        'ip': '192.168.1.159',
        'relay_states': [False, True]
    },
    'b': {
        'key': 'b',
        'name': 'Living Room',
        'ip': '192.168.1.218',
        'relay_states': [True, False]
    }
}

for source in sources.values():
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
    ssh.connect(source['ip'], username='pi', timeout=10, banner_timeout=10)
    source['ssh'] = ssh

class relays():
    def __init__(self, bb):
        self.bb = bb

    def set(self, states):
        for i in xrange(len(states)):
            state = states[i]
            bit = pow(2, i)
            if state:
                self.bb.port |= bit
            else:
                self.bb.port &= ~bit

# print("Vendor\t\tProduct\t\t\tSerial")
# dev_list = []
# for device in Driver().list_devices():
#     device = map(lambda x: x.decode('latin1'), device)
#     vendor, product, serial = device
#     #print "%s\t\t%s\t\t%s" % (vendor, product, serial)
#     print(vendor, "\t" , product, "\t", serial)
#
with BitBangDevice(device_id) as bb:
    rls = relays(bb)

    # get the curses screen window
    screen = curses.initscr()

    # turn off input echoing
    curses.noecho()

    # respond to keys immediately (don't wait for enter)
    curses.cbreak()

    # map arrow keys to special values
    screen.keypad(True)

    screen.addstr(0, 0, 'Keys:')
    screen.addstr(1, 0, '   a, b, x -> switch to A/B/X')
    screen.addstr(2, 0, '   A, B    -> guess A/B')
    screen.addstr(3, 0, '   q       -> quit')

    def switch_to(s):
        # mute all sources
        for source in sources.values():
            source['ssh'].exec_command('amixer sset Digital mute')

        # switch relay
        source = sources[s]
        rls.set(source['relay_states'])

        # unmute live source
        source['ssh'].exec_command('amixer sset Digital unmute')
        screen.addstr(7, 0, 'Listening to %s' % source['name'])
        screen.addstr(8, 0, '')
        pass

    def do_trial(i):
        screen.addstr(5, 0, 'Trial %d' % (i + 1))
        switch_to('a')
        while True:
            char = screen.getch()
            if char == ord('q'):
                return None
            char = chr(char)
            if char in ['a', 'b', 'x']:
                switch_to(char)
            if char in ['A', 'B']:
                return char.lower()

    results = []
    try:
        for i in xrange(int(sys.argv[1])):
            sources['x'] = random.choice([sources['a'], sources['b']])
            result = do_trial(i)
            if not result:
                break
            results.append([sources['x']['key'], result])
    finally:
        # shut down cleanly
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()

    print results
