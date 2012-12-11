#!/usr/bin/python

import numpy as np
from mce_control import mce_control
import time

USAGE="""
%prog [options] stage

Configure the MCE for open loop noise measurements.  Basically:
 - turns off a bunch of biases
 - disables the servo
 - disables muxing
 - for SQ1 measurements, sets a fixed feedback at the current lock point.

The "stage" argument indicates the highest stage you want to leave
biased.  I.e.:

   sa   - turn off sq2 biases.
   sq2  - turn off muxing, sq1 biases.
   sq1  - turn off muxing.  Requires a --row argument.

This program is not good at turning things on carefully.  It is mostly
for turning things off.  So you probably want to run mce_reconfig
before you run this, or pass "--reconfig" to have the program pre-run
it for you.
"""

from optparse import OptionParser
o = OptionParser(usage=USAGE)
o.add_option('--row', default=None, type=int)
o.add_option('--reconfig', action='store_true')
o.add_option('--frames', default=30, type=int)
opts, args = o.parse_args()

if len(args) != 1 or args[0] not in ['sa', 'sq2', 'sq1']:
    o.error("Provide a single stage argument (sa, sq2, sq1).")

stage = args[0]
if stage == 'sq1' and opts.row == None:
    o.error("The sq1 stage requires a --row argument.")

# Reconfigure?
if opts.reconfig:
    import os
    os.system('mce_reconfig')

# Get MCE
mce = mce_control()

if stage == 'sq1':
    # Check lock:
    print 'Columns that appear locked:'
    mce.data_mode(0)
    data = mce.read_data(opts.frames, row_col=True).data[opts.row,:,:]
    err, derr = data.mean(axis=-1), data.std(axis=-1)
    print (abs(err) < derr*2).astype('int')
    # Measure the feedback.
    mce.data_mode(1)
    data = mce.read_data(opts.frames, row_col=True).extract('fb')[opts.row,:,:]
    fb, dfb = data.mean(axis=-1), data.std(axis=-1)
    print 'Locking feedback:'
    print fb.astype('int')
    # Kill servo and set fb_const
    mce.fb_const(fb.astype('int'))
    mce.servo_mode(0)
    # There can be only one.  One row.
    sq1_bias = np.array(mce.read('ac', 'on_bias'))
    my_bias = sq1_bias[opts.row]
    sq1_bias[:] = 0
    sq1_bias[opts.row] = my_bias
    mce.write('ac', 'on_bias', sq1_bias)
    mce.write('ac', 'off_bias', sq1_bias)
    # Sleep for a bit to let those biases get written, then disable mux.
    time.sleep(.1)
    mce.write('ac', 'enbl_mux', [0])

if stage in ['sq2' or 'sa']:
    # Kill the SQ1 bias and disable mux.
    sq1_bias = mce.read('ac', 'on_bias')
    mce.write('ac', 'on_bias', np.zeros(len(sq1_bias), 'int'))
    mce.write('ac', 'off_bias', np.zeros(len(sq1_bias), 'int'))
    time.sleep(.1)
    mce.write('ac', 'enbl_mux', [0])

if stage == 'sa':
    # Kill the SQ2 bias
    sq2_bias = mce.read('sq2', 'bias')
    mce.write('sq2', 'bias', np.zeros(len(sq2_bias), 'int'))

# You will probably want error mode data.
mce.data_mode(0)

