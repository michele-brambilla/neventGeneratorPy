from nexus2event import *
from neventarray import *

import sys
import os
import errno
import numpy
import time

import zmq

def dummy(source):
    dataHeader = header(source)
    data = np.empty(shape=1,dtype=eventDt)
    data["ts"]=1234
    data["x"] = 23
    data["y"] = 4
    return dataHeader,data


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

def main(argv):
    source = argv[1]
    port = argv[2]

    dataHeader,data = loadNeXus2event(source).data
#    dataHeader,data = dummy(source)

    if len(sys.argv) > 3:
        data = multiplyNEventArray(data,int(argv[3]))

    print "Ready to send data"

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://127.0.0.1:"+port)
    
    count=0
    ctime=time.time()

    while(True):
        itime = time.time()

        zmq_socket.send_json(dataHeader)
        zmq_socket.send(data)

        print remaining
        if remaining > 0:
            time.sleep (remaining)

        count=count+1
        if time.time()-ctime > 10 :
            print count
            count = 0
            ctime = time.time()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
    main(sys.argv)


