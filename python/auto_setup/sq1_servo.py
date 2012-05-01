import time, os, glob
import auto_setup.util as util
from numpy import *
import numpy as np
from mce_data import MCERunfile, MCEFile

import servo

def go(tuning, rc, filename=None, fb=None, slope=None, gain=None):

    super_servo = tuning.get_exp_param('config_fast_sq2') or \
        tuning.get_exp_param('sq1_servo_all_rows')

    if not super_servo:
        f = open(os.path.join(tuning.base_dir, "row.init"), "w")
        for r in tuning.get_exp_param('sq2_rows'):
            f.write("%i\n" % r)
        f.close()
        f = open(os.path.join(tuning.base_dir, "sq2fb.init"), "w")
        for x in tuning.get_exp_param('sq2_fb'):
            f.write("%i\n" % x)
        f.close()

    ok, servo_data = acquire(tuning, rc, filename=filename, fb=fb,
                             gain=gain, super_servo=super_servo)
    if not ok:
        raise RuntimeError, servo_data['error']

    sq = SQ1Servo(servo_data['filename'], tuning=tuning)
    lock_points = sq.reduce()
    if tuning.get_exp_param('tuning_do_plots'):
        plot_out = sq.plot()
        tuning.register_plots(*plot_out['plot_files'])

    # Return dictionary of relevant results
    lock_points['super_servo'] = super_servo
    lock_points['data_shape'] = sq.data_shape
    lock_points['cols'] = sq.cols
    return lock_points


def acquire(tuning, rc, filename=None, fb=None,
            gain=None, super_servo=False, old_servo=False):

    # File defaults
    if filename == None:
        filename, acq_id = tuning.filename(rc=rc, action='sq1servo')
    else:
        try:
            acq_id = str(int(filename.split('_')[0]))
        except ValueError:
            acq_id = str(time.time())

    if super_servo:
        cmd = [tuning.bin_path+'sq1servo_all', '-p', 50]
    else:
        cmd = [tuning.bin_path+'sq1servo']

    if old_servo:
        # FB
        if fb == None:
            fb = {}
            for k in ['start','count','step']:
                fb[k] = tuning.get_exp_param('sq1_servo_flux_%s'%k)
        if gain == None:
            if rc == 's':
                rci = 0
            else:
                rci = int(rc) - 1
            gain = tuning.get_exp_param('sq1_servo_gain')[rci*8]
    
        # This syntax is for pre-2010 servo programs that only do one gain.
        cmd += ['-E0', filename, 0,0,0,
                fb['start'], fb['step'], fb['count'],
                rc, 0, tuning.get_exp_param("default_num_rows"), gain, 1]
    else:
        cmd += ['-p', 50, '-E1', rc, filename]

    status = tuning.run(cmd)
    if status != 0:
        return False, {'error': 'command failed: %s' % str(cmd)}

    # Register this acquisition, taking nframes from runfile.
    fullname = os.path.join(tuning.base_dir, filename)
    rf = MCERunfile(fullname + ".run")
    n_frames = rf.Item('par_ramp', 'par_step loop1 par1', type='int')[2] * \
        rf.Item('par_ramp', 'par_step loop2 par1', type='int')[2]
    
    tuning.register(acq_id, 'tune_servo', fullname, n_frames)
    
    return True, {'basename': acq_id,
                  'filename': fullname }

def acquire_all_row_painful(tuning, rc, filename=None, fb=None,
                            gain=None, old_servo=False):
    """
    For non-fast switching systems, acquire SQ1 servo data for all
    rows using repeated invocations of single row servos.  Then
    rewrite the data as if it were a single servo, to trick everyone.
    """
    # File defaults
    if filename == None:
        filename, acq_id = tuning.filename(rc=rc, action='sq1servo')
    else:
        try:
            acq_id = str(int(filename.split('_')[0]))
        except ValueError:
            acq_id = str(time.time())
    # Call standard acquire
    results = []
    for row in range(tuning.get_exp_param('num_rows')):
        # Imitate filenames of a real all row servo
        ok, r = acquire(tuning, rc, filename=filename+'.r%02i'%row,
                        fb=fb, gain=gain, super_servo=False, old_servo=old_servo)
        if not ok:
            print r
            return ok, r
        results.append(r)

    # Link the row0 runfile/data to masquerade as a single acq.
    target = '%s/%s' % (tuning.base_dir, filename)
    os.symlink(target + '.r00', target)
    os.symlink(target + '.r00.run', target + '.run')

    return True, {'basename': results[0]['basename'],
                  'filename': target }



class SQ1Servo(servo.SquidData):
    stage_name = 'SQ1Servo'
    xlabel = 'SQ1 FB / 1000'
    ylabels = {'data': 'SQ2 FB / 1000',
               'error': 'Error / 1000'}

    bias_assoc = 'row'

    def __init__(self, filename=None, tuning=None):
        servo.SquidData.__init__(self, tuning=tuning)
        self.data_attrs.append('error')
        if filename != None:
            self.read_data(filename)

    def _read_super(self, filename):
        """
        Helper for read_data that assembles array of data from all-row
        sq1servo .bias files.
        """
        data = []
        for n_row in range(64):
            f = '%s.r%02i.bias' % (filename, n_row)
            if not os.path.lexists(f):
                break
            data.append(util.load_bias_file(f))
        self.gridded = True
        self.error = array([a for a,_ in data])
        self.data = array([a for _,a in data])
        self.rows = array([i for i in range(n_row)])
        n_bias, _, n_col, n_fb = self.data_shape
        self.data = self.data.reshape(n_row*n_col,n_bias,n_fb). \
            transpose([1,0,2]).reshape(-1, n_fb)
        self.error = self.error.reshape(n_row*n_col,n_bias,n_fb). \
            transpose([1,0,2]).reshape(-1, n_fb)
        self.data_shape = n_bias, n_row, n_col, n_fb

    def _read_single(self, filename):
        """
        Helper for read_data that loads a single-row sq1servo file.
        """
        self.error, self.data = util.load_bias_file(filename+'.bias')
        # Awkward indexing...
        col_idx = self.cols - (amin(self.cols) / 8)*8
        self.rows = array(self.rf.Item('servo_init', 'row.init', type='int'))[col_idx]
        n_row = 1
        self.gridded = False
        n_bias, _, n_col, n_fb = self.data_shape
        self.data = self.data.reshape(n_row*n_col,n_bias,n_fb). \
            transpose([1,0,2]).reshape(-1, n_fb)
        self.error = self.error.reshape(n_row*n_col,n_bias,n_fb). \
            transpose([1,0,2]).reshape(-1, n_fb)

    def read_data(self, filename):
        """
        Loads an sq1servo data set.  Can probably figure out if there is
        multi-row data present and do The Right Thing.
        """
        rf = MCERunfile(filename+'.run')
        self.rf = rf
        self.data_origin = {'filename': filename,
                            'basename': filename.split('/')[-1]}
        # Record the columns
        rcs = rf.Item('FRAMEACQ', 'RC', type='int')
        self.cols = array([i+(rc-1)*8 for rc in rcs for i in range(8)])

        # Fix me: runfile always indicates bias was ramped, even though it usually wasn't
        bias_ramp = (rf.Item('par_ramp', 'par_title loop1 par1', \
                                 array=False).strip() == 'sq1bias')
        if bias_ramp:
            bias0, d_bias, n_bias = rf.Item('par_ramp', 'par_step loop1 par1', type='int')
            fb0, d_fb, n_fb = rf.Item('par_ramp', 'par_step loop2 par1', type='int')
            self.bias_style = 'ramp'
            self.bias = bias0 + d_bias*arange(n_bias)
        else:
            fb0, d_fb, n_fb = rf.Item('par_ramp', 'par_step loop1 par1', type='int')
            n_bias = 1
        # This should just extend the else; the second clause is a bug work-around
        if not bias_ramp or (bias_ramp and n_bias == 1):
            self.bias_style = 'select'
            row_order = np.array(rf.Item('HEADER', 'RB ac row_order', type='int'))
            # Delay setting self.bias until we know what rows are involved...

        self.d_fb = d_fb
        self.fb = fb0 + arange(n_fb) * d_fb

        # Prime
        self.data_shape = (n_bias, 1, len(self.cols), n_fb)

        # Attempt load after counting bias/fb steps
        if len(glob.glob(filename+'.bias')):
            self._read_single(filename)
        else:
            self._read_super(filename)

        if not bias_ramp or (bias_ramp and n_bias == 1):
            idx = row_order[self.rows]
            self.bias = array(rf.Item('HEADER', 'RB sq1 bias', type='int'))[idx]

    # This is different from servo.SquidData.reduce1 because for
    # multi-bias we pick a per-row best bias.
    def reduce1(self, slope=None):
        """
        Compute peak-to-peak response, store in self.analysis.
        """
        self._check_data()
        self._check_analysis(existence=True)
        span = amax(self.data, axis=-1) - amin(self.data, axis=-1)
        self.analysis['y_span'] = span
        if self.bias_style == 'ramp':
            # Identify bias index of largest response in each row
            select = span.reshape(self.data_shape[:-1]).max(axis=-1).argmax(axis=0)
            self.analysis['y_span_select_row'] = select
        self.analysis['select_row_sel']
        return self.analysis

    def reduce(self, slope=None, lock_amp=True):
        self._check_data()
        self._check_analysis(existence=True)
        
        if slope == None:
            # Dodge possiblity that params are different lengths...
            s1 = self.tuning.get_exp_param('default_servo_i')[self.cols]
            s2 = self.tuning.get_exp_param('sq1_servo_gain')[self.cols]
            slope = -sign(s1*s2)
        if not hasattr(slope, '__getitem__'):
            slope = array([slope]*len(self.cols))

        # Make slope either a scalar, or 1 value per curve.
        if any(slope != slope[0]):
            z = zeros(self.data.shape[:-1]).reshape(-1, len(slope))
            slope = (z + slope).ravel()
        else:
            slope = slope[0]
        n_fb = len(self.fb)
        an = servo.get_lock_points(self.data, scale=n_fb/40,
                                   lock_amp=lock_amp, slope=slope)
        # Add feedback keys
        for k in ['lock', 'left', 'right']:
            an[k+'_x'] = self.fb[an[k+'_idx']]

        # Tweak feedback values and rescale slopes
        d_fb = self.fb[1] - self.fb[0]
        an['lock_x'] += (d_fb * an['lock_didx']).astype('int')
        an['lock_slope'] /= d_fb

        self.analysis = an
        return an
        
    def plot(self, plot_file=None, format=None, data_attr='data'):
        if plot_file == None:
            plot_file = os.path.join(self.tuning.plot_dir, '%s' % \
                                         (self.data_origin['basename']))
        if format == None:
            format = self.tuning.get_exp_param('tuning_plot_format')

        # Is this a multi-bias ramp?  If so, split down
        if self.bias_style == 'ramp':
            ss = self.split()
            plot_files = []
            _format = format
            if format == 'pdf':  # make one big pdf
                _format = 'svg'
            for i,s in enumerate(ss):
                s.reduce()
                p = s.plot(plot_file=plot_file+'_b%02i'%i, format=_format,
                           data_attr=data_attr)
                plot_files += p['plot_files']
            # collate into pdf?
            if format == 'pdf':
                ofile = plot_file + '_all.pdf'
                pp = util.plotter.pdfCollator(plot_files, ofile)
                if pp.collate(remove_sources=True):
                    plot_files = [ofile]
            return {'plot_files': plot_files}

        # Now worry about whether we have analysis and data...
        self._check_data()
        self._check_analysis()

        # Display biases as inset text
        n_row, n_col = self.data_shape[-3:-1]
        idx = np.arange(n_row*n_col) 
        if self.bias_assoc == 'row':
            idx /= n_col
        elif self.bias_assoc == 'col':
            idx %= n_col
        ## make one string per bias...
        insets = ['BIAS = %5i' % b for b in self.bias]
        ## then repeat it as needed
        insets = [insets[i] for i in idx]

        # Default data is self.data
        data = getattr(self, data_attr)

        # Plot plot plot
        return servo.plot(

            self.fb, data, self.data_shape[-3:-1],
            self.analysis, plot_file,
            slopes=True,
            insets=insets,
            title=self.data_origin['basename'],
            xlabel=self.xlabel,
            ylabel=self.ylabels[data_attr],
            format=format,
            )

    def plot_error(self, *args, **kwargs):
        if not 'data_attr' in kwargs:
            kwargs['data_attr'] = 'error'
        if not 'plot_file' in kwargs:
            kwargs['plot_file'] = os.path.join(self.tuning.plot_dir, '%s' % \
                                  (self.data_origin['basename'] + '_err'))
        return self.plot(*args, **kwargs)


class SQ1ServoSA(SQ1Servo):
    stage_name = 'SQ1ServoSA'
    xlabel = 'SQ1 FB / 1000'
    ylabels = {'data': 'SA FB / 1000',
               'error': 'Error / 1000'}

    bias_assoc = 'rowcol'

    def read_data(self, filename):
        """
        Loads an sq1servo_sa data set.
        """
        rf = MCERunfile(filename+'.run')
        self.rf = rf
        self.data_origin = {'filename': filename,
                            'basename': filename.split('/')[-1]}

        # Determine columns, biases, feedbacks involved in servo
        self.load_ramp_params('RB sq1 bias')

        # Prime
        self.data_shape = (-1, 1, len(self.cols), len(self.fb))

        # Attempt load after counting bias/fb steps
        self._read_super_bias(filename)

    def reduce1(self, slope=None):
        """
        """
        self._check_data()
        self._check_analysis(existence=True)

        # We actually need to assess curve quality here; ask for
        # non-trivial lock-points.  Let's do two tests.
        # 1. Is there a V-phi (identified non trivial maximum and minimum)
        # 2. Are there too many zero-crossings?
        ok = np.zeros(self.data.shape[0], 'bool')
        r = []
        for i in range(len(self.data)):
            reg = servo.get_curve_regions(self.data[i], pairs=True)
            if i == 100: print reg
            # reg will always have at least 4 entries.  Remove any
            # trivial ones though.
            while len(reg) > 0 and reg[0][0] == reg[0][1]:
                reg.pop(0)
            while len(reg) > 0 and reg[-1][0] == reg[-1][1]:
                reg.pop(-1)
            # Now insist on at least 4 real features.  That's 1 phi0.
            if len(reg) < 4:
                continue
            # Also ask for a relatively small number of zero crossings
            dy = self.data[i] - self.data[i].mean()
            nz = (dy[1:] * dy[:-1] < 0).sum()
            if nz > 50:
                continue
            ok[i] = True
        self.reg = reg
        self.analysis['ok'] = ok

        span = amax(self.data, axis=-1) - amin(self.data, axis=-1)
        self.analysis['y_span'] = span
        if self.bias_style == 'ramp':
            # Identify bias index of largest response in each row
            #select = span.reshape(self.data_shape[:-1]).max(axis=-1).argmax(axis=0)
            #self.analysis['y_span_select_row'] = select
            dshape = self.data_shape[:-1]
            n_bias, n_row, n_col = dshape
            n_det = n_row * n_col
            # Count good curves in each column
            ok = self.analysis['ok'].reshape(n_bias, n_det)
            n_ok = ok.sum(axis=0)
            bias_idx = np.zeros(n_det, 'int')
            bias_ok = np.zeros(n_det, 'bool')
            # Get the best bias for each row/col
            span = span.reshape(n_bias, -1)
            for i in range(ok.shape[1]):
                if n_ok[i] > 0:
                    bias_idx[i] = np.argmax(ok[:,i] * span[:,i])
                    bias_ok[i] = True
            self.analysis['select_rowcol_sel'] = bias_idx
            self.analysis['select_rowcol_ok'] = n_ok > 0

        return self.analysis

    def reduce(self, slope=None, lock_amp=True):
        self._check_data()
        self._check_analysis(existence=True)
        
        if slope == None:
            # Dodge possiblity that params are different lengths...
            s1 = self.tuning.get_exp_param('default_servo_i')[self.cols]
            s2 = self.tuning.get_exp_param('sq1_servo_gain')[self.cols]
            slope = -sign(s1*s2)
        if not hasattr(slope, '__getitem__'):
            slope = array([slope]*len(self.cols))

        # Make slope either a scalar, or 1 value per curve.
        if any(slope != slope[0]):
            z = zeros(self.data.shape[:-1]).reshape(-1, len(slope))
            slope = (z + slope).ravel()
        else:
            slope = slope[0]
        n_fb = len(self.fb)
        an = servo.get_lock_points(self.data, scale=n_fb/40,
                                   lock_amp=lock_amp, slope=slope)

        # Add feedback keys
        for k in ['lock', 'left', 'right']:
            an[k+'_x'] = self.fb[an[k+'_idx']]

        # Tweak feedback values and rescale slopes
        d_fb = self.fb[1] - self.fb[0]
        an['lock_x'] += (d_fb * an['lock_didx']).astype('int')
        an['lock_slope'] /= d_fb

        self.analysis = an
        return an
        
