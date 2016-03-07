import sys
import os
import errno

import numpy as np
#from collections import namedtuple

import nxs
import neventarray


def loadAMOR(source) :
    f = nxs.open(source,'r')

    # retrieve data
    f.openpath("entry1/AMOR/area_detector/data")
    dim,datatype= f.getinfo()
    size = np.prod(dim)
    data = f.getdata()
    f.close()

    f = nxs.open(source,'r')
    f.openpath("entry1/AMOR/area_detector/time_binning")
    tof = f.getdata()
    f.close()

    nEvents = np.sum(data)
    signal = np.empty(nEvents,dtype=neventarray.eventDt)
#    timeStamp = np.empty(nEvents)
#    signal = np.append(signal,[1234,0,1,2])

    nEv = 0
    detID = 0
    for row in range(dim[0]):
        for col in range(dim[1]):
#            detID=detID+1
            for it in range(dim[2]):
                events = data[row][col][it]
                if events > 0:
                    signal[nEv:nEv+events]["ts"] = round(tof[it]/10.)
                    signal[nEv:nEv+events]["x"] = row
                    signal[nEv:nEv+events]["y"] = col
#                    detectorID[nEv:nEv+events] = detID
#                    timeStamp[nEv:nEv+events] = round(tof[it]/10.)
                    nEv = nEv+events

    if not signal.shape[0] == nEv:
        raise Exception("Error in reading NeXus data: wrong number of events",nEv)

#    return NEventArray(detectorID,timeStamp)
    return signal



def header(src):
    dataHeader = {
        "htype":"sinq-1.0",
        "mode":"pos",
        "pid":0,
        "hws":{"error":0,"overflow":0,"abc":432,"state1":1092,"state2":1092},
        "st":1457097133,
        "ts":123456789,
        "tr":10000,
        "ds":[{"ts":32,"cnt":1,"rok":1,"bsy":1,"sev":1,"pad":12,"x":16,"y":16},296]
        }
    return dataHeader


class loadNeXus2event:
    def __init__(self,source):
        self.source = source
        self.data = self.load()

    def load(self):
        if not os.path.isfile(self.source) :
            raise IOError

        print "Loading from file " + self.source
        return header(self.source),loadAMOR(self.source)



