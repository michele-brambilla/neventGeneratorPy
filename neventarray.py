import numpy as np

event_t = np.dtype([("ts",np.uint32),
                    ("sync",np.uint16),
                    ("x",np.uint16),
                    ("y",np.uint16)])

debug_t = np.dtype([("ts",np.uint32),
                    ("other",np.uint32)])

def multiplyNEventArray(data,multiplier) :
    return np.tile(data,multiplier)
