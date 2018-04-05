# This script supports ABX testing using an FT245RL based USB relay like these:
#
# https://smile.amazon.com/gp/product/B074MPWFF3/ref=oh_aui_search_detailpage?ie=UTF8&psc=1
# https://smile.amazon.com/SainSmart-Channel-Automation-Arduino-Raspberry/dp/B00J1DY32I/ref=sr_1_2?s=electronics&ie=UTF8&qid=1522964707&sr=1-2&keywords=sainsmart+usb+relay
#
# Documentation for one such relay can be found at http://s3.amazonaws.com/s3.image.smart/download/101-70-118/20-018-910.rar
#
# Dependencies:
#    pip install pylibfti
#    brew install libftdi
#
# Note - if you get an error about "libftdi not found", you might need to run as sudo/root
#
# Example command-line:
#    sudo python pyabx.py A90799W0 10 "MacBook Air" "Magni 3"
#
# To use, hook up source A to the Off position of relays 1 and 2 and source B
# to the On position of relays 1 and 2 (2 relays used for L/R channels).
#
# Don't forget to volume match before running your test, and keep the relays
# out of sight so you can't see the LEDs.

import curses
import random
import sys
import time
import math

# pip install pylibftdi
# brew install libftdi
from pylibftdi import Driver
from pylibftdi import BitBangDevice

from ctypes.util import find_library

if len(sys.argv) != 5:
    print "Please specify <relay device id> <num trials> <a label> <b label>"
    print ""
    print "---- Connected USB relays ----"
    for device in Driver().list_devices():
        device = map(lambda x: x.decode('latin1'), device)
        vendor, product, serial = device
        print('%s - %s (%s)' % (serial, product, vendor))
    sys.exit(1)

device_id = sys.argv[1]

trials = int(sys.argv[2])
source_names = {
    'a': sys.argv[3],
    'b': sys.argv[4],
    'x': 'Unknown',
}

relay_states = {
    'a': [False, False, False, False],
    'b': [True, True, False, False],
}
x = 'a'

# See https://en.wikipedia.org/wiki/ABX_test#Confidence
meaningful_at = {
    10: 9,
    11: 9,
    12: 10,
    13: 10,
    14: 11,
    15: 12,
    16: 12,
    17: 13,
    18: 13,
    19: 14,
    20: 15,
    21: 15,
    22: 16,
    23: 16,
    24: 17,
    25: 18,
}

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

    def switch_to(source):
        global extra_state

        states = relay_states[source]
        # add a toggle on the 3rd and 4th relays to keep consistent switching
        # noise to avoid bias
        for i in range(2, 4):
            states[i] = not states[i]
        rls.set(states)
        screen.addstr(7, 0, 'Listening to %s' % source_names[source].ljust(30))
        screen.addstr(8, 0, '' if trials >= 10 else 'too few trials to be meaningful, please run at least 10 trials')

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
    total_correct = 0
    try:
        for i in xrange(trials):
            x = random.choice(['a', 'b'])
            relay_states['x'] = relay_states[x]
            result = do_trial(i)
            if not result:
                break
            results.append([i+1, source_names[x], source_names[result], 'x' if x == result else ''])
            if x == result:
                total_correct += 1
    finally:
        # shut down cleanly
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()

    percent_correct = total_correct * 100 / trials
    meaningful = False
    if trials >= 10 and trials <= 25:
        meaningful = total_correct >= meaningful_at[trials]
    elif trials > 25:
        meaningful = total_correct > (trials / 2 + math.sqrt(trials))
    results.insert(0, ["Trial", "Actual", "Guess", "Correct"])
    for result in results:
        print '{0: <10} {1: <30} {2: <30} {3: <10}'.format(*result)
    print ""
    print "%f%% correct: %s" % (percent_correct, "statistically meaningful, you can tell the difference! :)" if meaningful else "not statistically meaningful, you can't tell the difference. :(")
