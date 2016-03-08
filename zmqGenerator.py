from nexus2event import *
from neventarray import *

import sys
import os
import errno
import numpy
import time

import zmq
import twisted
from twisted.internet.defer import inlineCallbacks

def dummy(source):
    dataHeader = header(source)
    data = np.empty(shape=1,dtype=eventDt)
    data["ts"]=1234
    data["x"] = 23
    data["y"] = 4
    return data


def usage() :
    print ""
    print "Usage:"
    print "\tpython "+sys.argv[0]+" <nexus file> <port> (<multiplier>)"
    print ""
    sys.exit(-1)

def sendEvent(socket,data,h) :
#    print h
    socket.send_json(h)
#    print data.itemsize
    socket.send(data)

def main(argv,mock=False):
    source = argv[1]
    port = argv[2]

    if not mock:
        data = loadNeXus2event(source)
    else:
        data = dummy(source)

    if len(sys.argv) > 3:
        data = multiplyNEventArray(data,int(argv[3]))

    print "Ready to send data"

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://127.0.0.1:"+port)
    
    global count
    count = 0
    ctime=time.time()
    size = data.size*eventDt.itemsize+sys.getsizeof(header())
    pulseID=0

    while(True):
        itime = time.time()

        dataHeader=header(pulseID,itime)

#        @inlineCallbacks
        def send_data():
            global count
            zmq_socket.send_json(dataHeader)
            zmq_socket.send(data)
            count += 1
        send_data()

        elapsed = time.time() - itime
        remaining = 1./14-elapsed

        if remaining > 0:
            time.sleep (remaining)

        pulseID += 1

        if time.time()-ctime > 10 :
            print "Sent ",count," events @ ",size*count/(10.*1e6)," MB/s"
            count = 0
            ctime = time.time()



if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
    main(sys.argv)


