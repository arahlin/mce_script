from auto_setup.config import mas_param

import numpy
import os

class DeadMask:
    def __init__(self, filename=None, label='', shape=None):
        """
        Provide filename to load dead mask, or pass dimensions in 'shape' to
        create empty mask.  Label may be consumed by plotters, etc.
        """
        if filename != None:
            self.read(filename)
        elif shape != None:
            self.shape = shape
            self.data = numpy.zeros(shape, dtype='int')
        self.label = label

    def read(self, filename):
        nr = mas_param(filename, 'n_rows', 0)
        nc = mas_param(filename, 'n_cols', 0)
        d = mas_param(filename, 'mask', 0)
        if nr==None or nc==None or d==None:
            raise RuntimeError, 'Invalid or missing dead_mask file "%s"' % filename
        self.data = d.reshape(nc, nr).transpose()
        self.shape = self.data.shape

    def str(self):
        s = 'n_rows = %i;\nn_cols = %i;\n\n' % (self.shape)
        s += 'mask = [\n' \
            '   /* rows:'
        for r in range(self.shape[0]):
            if r%10 == 0: s+= ' '
            s += ' %i' % (r%10)
        s += ' */\n'
        for c in range(self.shape[1]):
            s+=  '   /*c%02i*/  ' % c
            for r in range(self.shape[0]):
                if r%10 == 0: s+= ' '
                s += '%i,' % self.data[r,c]
            s += '\n'
        s = s[:-2] + ' ];\n'
        return s

    def write(self, filename, comment=None):
        f = open(filename, 'w')
        if comment != None:
            if comment[-1] != '\n': comment += '\n'
            f.write(comment)
        f.write(self.str())
        f.close()
        

def get_all_dead_masks(tuning, union=False):
    """
    Discover and load all dead masks.  Returns list of DeadMask objects.
    """
    mask_list = ["squid1", "multilock", "jumper", "connection", "other"]
    mask_files = [ os.environ["MAS_TEMPLATE"] + os.path.join("dead_lists",
            tuning.get_exp_param("array_id"), "dead_" + m + ".cfg") for m in
            mask_list ]
    mask_files = [m for m in mask_files if os.path.exists(m)]
    masks = [DeadMask(f, label=l) for f,l in zip(mask_files, mask_list)]
    if union:
        if len(masks) == 0:
            return None
        mask = DeadMask(shape=masks[0].shape, label='union')
        mask.data = sum([m.data for m in masks]).astype('bool').astype('int')
        return mask
    return masks

