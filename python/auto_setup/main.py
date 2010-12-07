import util
import series_array
import sq2_servo
import sq1_servo
import sq1_ramp
import frame_test

import os
import subprocess
import time
import shutil
from numpy import *


def do_init(tuning, rcs, check_bias, ramp_sa_bias, note):
    # write a note file
    if (note != None):
        tuning.write_note(note)

    # initialise the squid tuning results file
    tuning.write_sqtune(link=True)

    # check whether the SSA and SQ2 biases have already been set
    on_bias = False
    if (check_bias):
        for c in rcs:
            exit_status = tuning.run(["check_zero", "rc%i" % (c), "sa_bias"])
            if (exit > 8):
                print "check_zero failed with code", exit_status
            on_bias += exit_status

    # experiment.cfg setting may force a ramp_sa_bias.
    if (ramp_sa_bias == None):
        ramp_sa_bias = tuning.get_exp_param("sa_ramp_bias")

    if (tuning.get_exp_param("tes_bias_do_reconfig") != 0):
        # setting detectors bias by first driving them normal and then
        # to the transition.
        cfg_tes_bias_norm = tuning.get_exp_param("tes_bias_normal")
        for i,x in enumerate(cfg_tes_bias_norm):
            tuning.cmd("wra tes bias %i %s" % (i, x))

        time.sleep(tuning.get_exp_param("tes_bias_normal_time"))

        cfg_tes_bias_idle = tuning.get_exp_param("tes_bias_idle")
        tuning.set_exp_param("tes_bias", cfg_tes_bias_idle)
        for i,x in enumerate(cfg_tes_bias_idle):
            tuning.cmd("wra tes bias %i %s" % (i, x))

    # load squid biases from config file default parameters
    def_sa_bias = tuning.get_exp_param("default_sa_bias")
    sq2_bias = tuning.get_exp_param("default_sq2_bias")
    sq1_bias = tuning.get_exp_param("default_sq1_bias")
    sq1_bias_off = tuning.get_exp_param("default_sq1_bias_off")

    # Load default values for biases
    tuning.set_exp_param("sa_bias", def_sa_bias)
    tuning.set_exp_param("sq2_bias", sq2_bias)
    tuning.set_exp_param("sq1_bias", zeros([len(sq1_bias)]))
    tuning.set_exp_param("sq1_bias_off", zeros([len(sq1_bias_off)]))

    # data_mode and servo_mode and write.
    prepare_mce(tuning, run_now=True)

    # if the ssa and sq2 biases were previously off the system waits for
    # thermalisation

    if (check_bias and on_bias == 0):
        print "Waiting for thermalisation."
        time.sleep(210)

    return {"ramp_sa_bias": ramp_sa_bias, "sq1_bias": sq1_bias,
            "sq1_bias_off": sq1_bias_off, "sq2_bias": sq2_bias}

def prepare_mce(tuning, run_now=True):
    """
    Perform the minimal MCE configuration necessary in order to
    perform tuning ramps/servos.

    Basically, just set the data_mode and disable the MCE servo.
    """
    tuning.set_exp_param("servo_mode", 1)     # fb_const
    tuning.set_exp_param("flux_jumping", 0)   # safer
    tuning.set_exp_param("data_mode", 0)      # error mode.
    tuning.write_config(run_now=run_now)


#  do_*
#  
#  These functions execute a stage of the tuning.  Each is structured
#  in the same way; first the MCE is configured so that the spawned
#  program can do the work.  Then the ramper or servoer is spawned and
#  the data analyzed.  The results of the analysis are then used to
#  update the experiment.cfg file and MCE with new set/lock points.

def prepare_sa_ramp(tuning, cols=None):
    """
    Prepare the MCE to run the SA ramp.
    """
    # Get columns relevant to this tuning
    if cols == None:
        cols = array(tuning.column_list())
    
    # Disable servo and set data_mode to error only.
    tuning.set_exp_param("data_mode", 0)
    tuning.set_exp_param("servo_mode", 1)

    # Set the ADC_offsets to 0
    tuning.set_exp_param("config_adc_offset_all", 0)
    tuning.set_exp_param_range("adc_offset_c", cols, cols*0)

    # Set SQ2 and SQ1 biases to 0
    tuning.set_exp_param_range("sq2_bias", cols, cols*0)
    n_sq1 = len(tuning.get_exp_param('sq1_bias'))
    tuning.set_exp_param("sq1_bias", zeros(n_sq1))
    tuning.set_exp_param("sq1_bias_off", zeros(n_sq1))

    # Set the SA bias and offset to the default values
    offset_ratio = tuning.get_exp_param("sa_offset_bias_ratio")
    def_sa_bias = tuning.get_exp_param("default_sa_bias")
    def_sa_offset = (def_sa_bias * offset_ratio).astype('int')
    tuning.set_exp_param_range("sa_bias", cols, def_sa_bias[cols])
    tuning.set_exp_param_range("sa_offset", cols, def_sa_offset[cols])

    # Update settings.
    tuning.write_config()

def do_sa_ramp(tuning, rc, rc_indices, ramp_sa_bias=False):
    ok, ramp_data = series_array.acquire(tuning, rc,
                                         do_bias=ramp_sa_bias)
    if not ok:
        raise RuntimeError, ramp_data['error']

    sa = series_array.SARamp(ramp_data['filename'], tuning=tuning)
    if sa.bias_style == 'ramp':
        sa.reduce1()
        sa = sa.subselect() # replace with best bias version

    lock_points = sa.reduce()
    
    # Set-point results for feedback and ADC_offset
    fb, target = lock_points['lock_x'], lock_points['lock_y']
    tuning.set_exp_param_range("adc_offset_c", rc_indices, target)
    tuning.set_exp_param_range("sa_fb", rc_indices, fb)

    # Maybe the bias and SA offset, too.
    if ramp_sa_bias:
        offset_ratio = tuning.get_exp_param('sa_offset_bias_ratio')
        tuning.set_exp_param_range("sa_bias", rc_indices, sa.bias)
        tuning.set_exp_param_range("sa_offset", rc_indices,
                                   (offset_ratio * sa.bias).astype('int'))

    tuning.write_config()

    # Plot final curve only.
    plot_out = sa.plot()
    tuning.register_plots(*plot_out['plot_files'])

    return {"status": 0, "column_adc_offset": target}


def do_sq2_servo(tuning, rc, rc_indices, tune_data):
    def_sa_bias = tuning.get_exp_param("default_sa_bias")

    # Sets the initial SA fb (found in the previous step or set to mid-range)
    # for the SQ2 servo
    sa_fb_init = tuning.get_exp_param('sa_fb')
    f = open(os.path.join(tuning.base_dir, "safb.init"), "w")
    for x in sa_fb_init:
        f.write("%i\n" % x)
    f.close()

    # Set data mode, servo mode, turn off sq1 bias, set default sq2 bias
    tuning.set_exp_param("data_mode", 0)
    tuning.set_exp_param("servo_mode", 1)
    tuning.set_exp_param("sq1_bias", zeros([len(tune_data["sq1_bias"])]))
    tuning.set_exp_param("sq1_bias_off",
        zeros([len(tune_data["sq1_bias_off"])]))
    tuning.set_exp_param_range("sq2_bias", rc_indices,
            tune_data["sq2_bias"][rc_indices])

    if (tuning.get_exp_param("sq2_servo_bias_ramp") != 0):
        raise RuntimeError, "sq2_servo_bias_ramp is not yet supported..."

    # Update settings, acquire and analyze the ramp.
    tuning.write_config()
    sq2_data = sq2_servo.go(tuning, rc)

    # Save SQ2 set point (SA feedback) and SQ2 feedback
    tuning.set_exp_param_range("sa_fb", rc_indices, sq2_data["lock_y"])
    tuning.set_exp_param_range("sq2_fb", rc_indices, sq2_data["lock_x"])

    tuning.write_config()
    return {"status": 0}


def prepare_sq1_servo(tuning):
    # Standard
    tuning.set_exp_param("data_mode", 0)
    tuning.set_exp_param("servo_mode", 1)

    # Enable SQ1 bias
    sq1_bias = tuning.get_exp_param("default_sq1_bias")
    sq1_bias_off = tuning.get_exp_param("default_sq1_bias_off")
    tuning.set_exp_param("sq1_bias", sq1_bias)
    tuning.set_exp_param("sq1_bias_off", sq1_bias_off)

    # Set the ADC_offsets to their per-column values
    tuning.set_exp_param("config_adc_offset_all", 0)

    # Commit
    tuning.write_config()


def do_sq1_servo(tuning, rc, rc_indices):
   
    # Sets the initial SQ2 fb (found in the previous step or set to mid-range)
    # for the SQ1 servo
    #sq2_fb_init = tuning.get_exp_param('sq2_fb')
    sq2_fb_init = [8200] * (max(rc_indices)+1)
    f = open(os.path.join(tuning.base_dir, "sq2fb.init"), "w")
    for x in sq2_fb_init:
        f.write("%i\n" % x)
    f.close()

    sq1_data = sq1_servo.go(tuning, rc)
    
    # Load existing FB choices
    fb_nr = tuning.get_exp_param('array_width') # number of rows in sq2_fb_set
    fb_col = tuning.get_exp_param('sq2_fb')
    fb_set = tuning.get_exp_param('sq2_fb_set').reshape(-1, fb_nr).transpose() # r,c
    
    # Determine the SQ2 FB for each column, and if possible for each detector.
    cols = sq1_data['cols']
    if sq1_data['super_servo']:
        n_row, n_col = sq1_data['data_shape'][-3:-1]
        fb_set[:n_row,cols] = sq1_data['lock_y'].reshape(-1, n_col)
        # Get chosen row on each column
        rows = tuning.get_exp_param('sq2_rows')[cols]
        fb_col[cols] = array([ fb_set[r,c] for r,c in zip(rows, cols) ])
    else:
        # Analysis gives us SQ2 FB for chosen row of each column.
        fb_col[cols] = sq1_data['lock_y']
        n_row = tuning.get_exp_param("default_num_rows")
        fb_set[:,cols] = sq1_data['lock_y']
        
    # Save results
    tuning.set_exp_param('sq2_fb', fb_col)
    tuning.set_exp_param('sq2_fb_set', fb_set.transpose().ravel())

    tuning.write_config()
    return 0


def do_sq1_ramp(tuning, rcs, tune_data, init=True):

    tuning.set_exp_param("data_mode", 0)
    tuning.set_exp_param("servo_mode", 1)
    tuning.set_exp_param("config_adc_offset_all", 0)
    tuning.set_exp_param("sq1_bias", tune_data["sq1_bias"])
    tuning.set_exp_param("sq1_bias_off", tune_data["sq1_bias_off"])
    tuning.write_config()

    # Don't correct for sample_num!
    samp_num = tuning.get_exp_param("default_sample_num")
    array_width = tuning.get_exp_param("array_width")

    # Acquire ramp for each RC
    ramps = []
    for rc in rcs:
        ok, info = sq1_ramp.acquire(tuning, rc)
        if not ok:
            raise RuntimeError, 'sq1ramp failed for rc%s (%s)' % \
                (str(rc), info['error'])
        ramps.append(sq1_ramp.SQ1Ramp(info['filename']))

    # Join into single data/analysis object
    #... something is wrong here ...
    ramps = sq1_ramp.SQ1Ramp.join(ramps)
    ramps.tuning = tuning
    lock_points = ramps.reduce()
    n_row, n_col = ramps.data_shape[-3:-1]

    # Save new ADC offsets
    adc_col = tuning.get_exp_param('adc_offset_c')[ramps.cols].reshape(1,-1)
    adc_adj = (lock_points['lock_y']). \
        reshape(n_row, n_col).astype('int')
    new_adc = adc_col + adc_adj

    # Careful with index transposition here
    cv, rv = ix_(ramps.cols, ramps.rows)
    idx = (array_width * cv + rv).ravel()
    adc = tuning.get_exp_param('adc_offset_cr')
    adc[idx] = new_adc.transpose().ravel()

    # Note that adc_offset_cr needs to be corrected for samp_num
    tuning.set_exp_param('adc_offset_cr', adc/samp_num)
    tuning.set_exp_param('config_adc_offset_all', 1)
    tuning.write_config()

    # Produce plots
    masks = util.get_all_dead_masks(tuning)
    ramps.plot(dead_masks=masks)

    # Return analysis stuff so it can be stored in .sqtune...
    return ramps


def operate(tuning):
    """
    Mask dead detectors, enable the MCE servo, and set the default data mode.

    This should be run once the final ADC offsets have been chosen (sq1_ramp).
    """
    # Servo control
    tuning.set_exp_param("servo_mode", 3)
    tuning.set_exp_param("servo_p", tuning.get_exp_param("default_servo_p"))
    tuning.set_exp_param("servo_i", tuning.get_exp_param("default_servo_i"))
    tuning.set_exp_param("servo_d", tuning.get_exp_param("default_servo_d"))
    tuning.set_exp_param("flux_jumping", \
            tuning.get_exp_param("default_flux_jumping"))

    # Data mode, etc.
    tuning.set_exp_param("data_mode", tuning.get_exp_param("default_data_mode"))

    # Disable dog-housed column biases
    columns_off = tuning.get_exp_param("columns_off")
    bad_columns = columns_off.nonzero()[0]
    if len(bad_columns) > 0:
        tuning.set_exp_param_range("sa_bias", bad_columns, 0)
        tuning.set_exp_param_range("sq2_bias", bad_columns, 0)

    # Compile dead detector mask
    print "Assembling dead detector mask."
    mask = util.get_all_dead_masks(tuning, union=True)
    tuning.set_exp_param("dead_detectors", mask)

    # Write to MCE
    tuning.write_config(run_now=True)



def frametest_check(tuning, rcs, row, column):
    """
    Fix me.
    """
    # Permit row override, or else take it from config
    if (row == None):
        row = 9
        print "Row = %i is used for frametest_plot by default." % row

    if (len(rcs) < 4):
        for rc in rcs:
            lock_file_name, acq_id = tuning.filename(rc=rc, action="lock")
            frametest_plot(lock_file_name, column=column, row=row, rc=rc,
                    binary=1, acq_id=acq_id)
    else:
        lock_file_name, acq_id = tuning.filename(rc="s", action="lock")
        rc = 5
        frametest_plot(lock_file_name, column=column, row=row, rc=rc,
                binary=1, acq_id=acq_id)


def auto_setup(rcs=None, check_bias=False, short=False, ramp_sa_bias=None,
               note=None, reg_note=None, data_root=None,
               first_stage=None, last_stage=None,
               debug=False):
    """
Run a complete auto setup.

This metafunction runs, in turn, each of acquisition, tuning, and reporting
functions to perform an entire auto setup procedure, exactly like the old
IDL auto_setup_squids."""

    tuning = util.tuningData(data_root=data_root, reg_note=reg_note, debug=debug)
    print 'Tuning ctime: %i' % tuning.the_time

    # set_directory creates directories and files where to store the tuning data
    # and plots.
    if (not short):
        tuning.run(["set_directory", tuning.data_root], no_log=True)

    # Create data and analysis directories
    tuning.make_dirs()

    # Register plots for offload
    tuning.register_plots(init=True)

    # set rc list, if necessary
    if (rcs == None):
        print "  Tuning all available RCs."
        # Cards in sequence.
        #rcs = tuning.rc_list()
        # All cards at once.
        rcs = ['s']

    # default parameters
    if ramp_sa_bias == None:
        ramp_sa_bias = bool(tuning.get_exp_param('sa_ramp_bias'))

    # initialise the auto setup
    tune_data = do_init(tuning, rcs, check_bias, ramp_sa_bias, note)

    if (tune_data == None):
        return 1

    stages = ['sa_ramp',
              'sq2_servo',
              'sq1_servo',
              'sq1_ramp',
              'sq1_ramp_tes',
              'operate']
    
    # ramp tes bias and see open loop response?
    if tuning.get_exp_param("sq1_ramp_tes_bias") == 0 or short != 0:
        stages.remove('sq1_ramp_tes')
        
    if first_stage == None:
        if short == 1:
            first_stage = 'sq1_servo'
        if short == 2:
            first_stage = 'sq1_ramp'
    if first_stage == None:
        first_stage = stages[0]
    if last_stage == None:
        if (tuning.get_exp_param("stop_after_sq1_servo") == 1):
            last_stage = 'sq1_servo'
    if last_stage == None:
        last_stage = stages[-1]

    s0, s1 = stages.index(first_stage), stages.index(last_stage)
    stages = stages[s0:s1+1]
    
    for c in rcs:
        print "Processing rc%s" % str(c)
        if c == 's':
            rc_indices = array(tuning.column_list())
        else:
            rc_indices = 8 * (int(c) - 1) + arange(8)
        if 'sa_ramp' in stages:
            prepare_sa_ramp(tuning, cols=rc_indices)
            sa_dict = do_sa_ramp(tuning, c, rc_indices,
                                 ramp_sa_bias=ramp_sa_bias)
        if 'sq2_servo' in stages:
            s2_dict = do_sq2_servo(tuning, c, rc_indices, tune_data)
            if (s2_dict["status"] != 0):
                return s2_dict["status"]
        if 'sq1_servo' in stages:
            prepare_sq1_servo(tuning)
            e = do_sq1_servo(tuning, c, rc_indices)
            if (e != 0):
                return e

    if 'sq1_ramp' in stages:
        # sq1 ramp check
        sq1 = do_sq1_ramp(tuning, rcs, tune_data)
        tuning.write_sqtune(sq1_ramp=sq1)

    if 'sq1_ramp_tes' in stages:
        # ramp tes bias and see open loop response?
        print 'sq1_ramp_tes to-be-implemented...'
        #rtb_file_name, acq_id = tuning.filename(rc=rc, action="sq1rampb")
        #ramp_sq1_bias_plot(rtb_file_name, rc=rc, acq_id=acq_id)

    if 'frametest' in stages:
        # lock check
        print 'frametest_check to-be-implemented...'
        #frametest_check(tuning, rcs, row, column)

    if 'operate' in stages:
        # Enable servo
        operate(tuning)

    # Copy experiment.cfg and config script between main data dir and tuning dir.
    shutil.copy2(tuning.config_mce_file, os.path.join(tuning.data_dir,
                 "config_mce_auto_setup_" + tuning.current_data))
    shutil.copy2(tuning.exp_file, tuning.data_dir)

    t_elapsed = time.time() - tuning.the_time
    print "Tuning complete.  Time elapsed: %i seconds." % t_elapsed
    return 0