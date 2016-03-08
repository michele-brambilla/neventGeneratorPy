#ifndef _ZMQGENERATOR_H
#define _ZMQGENERATOR_H
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



class generatorSource:

    def __init__ (self,source,port,multiplier,mock=False):
        self.source = source
        self.port = port
        self.multiplier = multiplier
        self.context = zmq.Context()
        self.data = self.load(mock)
        self.socket = self.connect()
        self.count = 0
        self.run()

    def load(self,mock):
        if not mock:
            data = loadNeXus2event(self.source)
        else:
            data = self.dummy()

        if self.multiplier > 1:
            data = multiplyNEventArray(data,int(self.multiplier))

        return data

    def dummy(self):
        data = np.empty(shape=1,dtype=eventDt)
        data["ts"]=1234
        data["x"] = 23
        data["y"] = 4
        return data

    def connect(self):
        zmq_socket = self.context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://127.0.0.1:"+self.port)
        return zmq_socket

    def run(self):
        data = self.data
        ctime=time.time()
        pulseID=0
        
        while(True):
            itime = time.time()
            dataHeader=header(pulseID,itime)
            
            def send_data(socket,head):
                socket.send_json(head)
                socket.send(self.data)
                self.count += 1
                
            send_data(self.socket,dataHeader)

            elapsed = time.time() - itime
            remaining = 1./14-elapsed

            if remaining > 0:
                time.sleep (remaining)

            pulseID += 1

            if time.time()-ctime > 10 :
                size = (data.size*eventDt.itemsize+
                        sys.getsizeof(dataHeader))

                print "Sent ",self.count," events @ ",size*self.count/(10.*1e6)," MB/s"
                self.count = 0
                ctime = time.time()




def main(argv,mock=False):
    source = argv[1]
    port = argv[2]

    multiplier = 1
    if len(sys.argv) > 3:
        multiplier = argv[3]

    generatorSource(source,port,multiplier,mock=True)
    
#
#    if not mock:
#        data = loadNeXus2event(source)
#    else:
#        data = dummy(source)
#
#    if len(sys.argv) > 3:
#        data = multiplyNEventArray(data,int(argv[3]))
#
#    print "Ready to send data"
#
#    context = zmq.Context()
#    zmq_socket = context.socket(zmq.PUSH)
#    zmq_socket.bind("tcp://127.0.0.1:"+port)
#    
#    global count
#    count = 0
#    ctime=time.time()
#    size = data.size*eventDt.itemsize+sys.getsizeof(header())
#    pulseID=0
#
#    while(True):
#        itime = time.time()
#
#        dataHeader=header(pulseID,itime)
#
##        @inlineCallbacks
#        def send_data():
#            global count
#            zmq_socket.send_json(dataHeader)
#            zmq_socket.send(data)
#            count += 1
#        send_data()
#
#        elapsed = time.time() - itime
#        remaining = 1./14-elapsed
#
#        if remaining > 0:
#            time.sleep (remaining)
#
#        pulseID += 1
#
#        if time.time()-ctime > 10 :
#            print "Sent ",count," events @ ",size*count/(10.*1e6)," MB/s"
#            count = 0
#            ctime = time.time()
#


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
    main(sys.argv)



#endif //ZMQGENERATOR_H
