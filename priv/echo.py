#!/usr/bin/python

import sys
import time

last_line = "none"

while 1:
    line = sys.stdin.readline()
    if not line: break

    # Send back the received line
    print line,

    # Remember
    last_line = line

    # And finally, lets flush stdout because we are communicating with
    # Erlang via a pipe which is normally fully buffered.
    sys.stdout.flush()
