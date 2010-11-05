import auto_setup.util as util
from numpy import *
import biggles

def smooth(x, scale):
    s = x.shape
    x.shape = (-1, s[-1])
    y = array([convolve(xx, [1]*scale, mode='valid') for xx in x]) / scale
    x.shape = s
    y.shape = s[:-1] + (y.shape[-1],)
    return y

def get_lock_points(data, scale=0, yscale=None, lock_amp=False, slope=1.):
    # Smooth, differentiate, and truncate to same length
    if scale > 0:
        y = smooth(data, scale)
    x_offset = (scale+1)/2      # Later we will compensate
    dy = y[:,1:] - y[:,:-1]
    y = y[:,:-1]

    # Find first extremum in second half.
    lo = y.shape[1] / 2
    hi = y.shape[1]

    # Measure y-extent
    y_max, y_min = y[:,lo:hi].max(axis=1), y[:,lo:hi].min(axis=1)
    y_mid, y_amp = (y_max + y_min)/2, (y_max - y_min)/2
    yscale = y_amp * 0.05

    # Find all ineligible points with opposite derivative
    other_edge = (dy*slope < 0) #* \
    z = \
        (y_max.reshape(-1,1) - y > yscale.reshape(-1,1)) * \
        (y - y_min.reshape(-1,1) > yscale.reshape(-1,1))

    # Find a rising or falling region
    if slope < 0:
        i_right = y[:,lo:hi].argmin(axis=1) + lo
    else:
        i_right = y[:,lo:hi].argmax(axis=1) + lo

    # Find right-most such point that is to the left of i_right
    i_left = i_right*0
    for i, (p, r) in enumerate(zip(other_edge, i_right)):
        if any(p[scale:r-scale/2]):
            i_left[i] = p[:r-scale/2].nonzero()[0][-1]
    
    # Lock mid-way in y or x?
    if lock_amp:
        target = array([yy[a] + yy[b] for yy,a,b in zip(y, i_left, i_right)]) / 2
        lock_idx = []
        for a,b,tt,yy in zip(i_left, i_right, target, y):
            zz = (slope*(yy[a:b]-tt)>=0).nonzero()[0]
            if len(zz) == 0: zz = [(b-a)/2]
            lock_idx.append(zz[0]+a)
        lock_idx = array(lock_idx).astype('int')
    else:
        lock_idx = (i_left + i_right)/2
    lock_y = array([yy[i] for i,yy in zip(lock_idx, y)])
    lock_idx += x_offset
    
    return {'lock_idx': lock_idx,
            'lock_y': lock_y,
            'slope': slope,
            'left_idx': i_left,
            'right_idx': i_right,
            }

def period_correlation(y, width=None, normalize=True):
    n, nx = y.shape
    if width == None:
        width = nx / 2
    m = nx - width
    corr = zeros((n, m))
    for i in range(m):
        corr[:,i] = sum((y[:,nx-width-i:nx-i] - y[:,-width:])**2, axis=1)
    if normalize:
        # at some point we have to cross the other slope
        corr /= (y[:,-width:].std(axis=1)**2).reshape(-1,1)
    return corr

def period(y, width=None):
    """
    Determine periods of (V-phi) curves in y.
    """
    n0, n_x = y.shape
    if width == None:
        width = n_x / 2
    p = zeros(n0)
    corr = period_correlation(y, width=width)
    for i, c in enumerate(corr):
        # Each corr curve rises up from 0 to some maximum, then down
        # to "0" again, and repeat (or not).
        thresh = 3. # units are rms**2
        dc = c - thresh
        ups = ((dc[1:] > 0) * (dc[:-1] <= 0)).nonzero()[0]
        dns = ((dc[1:] < 0) * (dc[:-1] >= 0)).nonzero()[0]
        if len(ups) < 1 or len(dns) < 1:
            continue
        if len(ups) < 2: ups = [ups[0], len(c)]
        p[i] = dns[0] + argmin(c[dns[0]:ups[1]])
    return p

def add_curves(ax, x, y, lp, i,
               set_points=True, lock_levels=True, intervals=True,
               slopes=True, insets=True):
    if set_points and lp.haskey('lock_x'):
        ax.add(biggles.LineX(lp['lock_x'][i]*scale))
    if lock_levels and lp.haskey('lock_y'):
        ax.add(biggles.LineY(lp['lock_y'][i]*scale))
    if intervals and lp.haskey('left_x'):
        ax.add(biggles.LineX(lp['left_x'][i]*scale,type='dashed'))
    if intervals and lp.haskey('right_x'):
        ax.add(biggles.LineX(lp['right_x'][i]*scale,type='dashed'))
    if slopes:
        for d in ['up', 'dn']:
            if not lp.haskey('lock_%s_sl' % d): continue
            m,x0,y0 = [lp['lock_%s'%(e)][i]
                       for e in ['%s_sl'%d,'%s_x'%d,'y']]
            ax.add(biggles.Slope(m, (x0*scale,y0*scale),type='dashed'))


def plot(x, y, y_rc, lock_points, plot_file,
         shape=(4,2), img_size=None, scale=1./1000,
         title=None, xlabel=None, ylabel=None,
         titles=None,
         rows=None, cols=None,
         insets=None,
         lock_levels=True,
         set_points=False,
         intervals=False,
         slopes=False,
         scale_style='tight',
         label_style='row_col',
         ):

    nr, nc = y_rc
    cl, rl, rcl = False, False, False
    if label_style == 'col_only':
        cl = True
    elif label_style == 'row_col':
        rcl = True

    pl = util.plotGridder(y_rc, plot_file, title=title, xlabel=xlabel, ylabel=ylabel,
                          target_shape=shape, img_size=img_size,
                          col_labels=cl, rowcol_labels=rcl)
            
    for r, c, ax in pl:
        if r >= nr or c >= nc: continue
        i = c + r*nc
        if set_points:
            ax.add(biggles.LineX(lock_points['lock_x'][i]*scale))
        if lock_levels:
            ax.add(biggles.LineY(lock_points['lock_y'][i]*scale))
        if intervals:
            ax.add(biggles.LineX(lock_points['left_x'][i]*scale,type='dashed'))
            ax.add(biggles.LineX(lock_points['right_x'][i]*scale,type='dashed'))
        if slopes:
            for d in ['up', 'dn']:
                m,x0,y0 = [lock_points['lock_%s'%(e)][i]
                           for e in ['%s_sl'%d,'%s_x'%d,'y']]
                ax.add(biggles.Slope(m, (x0*scale,y0*scale),type='dashed'))
        if insets != None:
            ax.add(biggles.PlotLabel(0., 0., insets[i],
                                         halign='left',valign='bottom'))
        ax.add(biggles.Curve(x/1000., y[i]/1000.))

        if scale_style == 'roll-off':
            # Prevent small signals from causing large tick labels
            hi, lo = amax(y[i])/1000, amin(y[i])/1000
            if hi - lo < 4:
                mid = (hi+lo)/2
                ax.yrange = (mid-2, mid+2)
        elif scale_style == 'tight':
            hi, lo = amax(y[i]) / 1000., amin(y[i]) / 1000.
            dx = (hi - lo)*.1
            ax.yrange = lo - dx, hi + dx
            ax.xrange = x[0]/1000., x[-1]/1000.
    return {
        'plot_files': pl.plot_files,
        }
