import numpy as np

event_t = np.dtype([("ts",np.uint32),
                    ("sync",np.uint16),
                    ("x",np.uint16),
                    ("y",np.uint16)])

def multiplyNEventArray(data,multiplier) :
#    return NEventArray(np.tile(data[0],multiplier), 
#                       np.tile(data[1],multiplier))
    return np.tile(data,multiplier)
