import time
import zmq
import sys
import numpy as np
import json

from neventarray import *

class generatorReceiver :
    def __init__ (self, fulladdress) :
        self.fulladdress = fulladdress
        self.count = 0
        self.context = zmq.Context()
        self.socket = self.connect()
        self.run()


    def connect(self) :
        zmq_socket = self.context.socket(zmq.PULL)
        zmq_socket.connect(self.fulladdress)
        return zmq_socket

    def run(self) :
        ctime=time.time()
        pulseID = 0
        while(True):

            dataHeader = self.socket.recv_json()
            buf = self.socket.recv(copy=True)
            data = np.frombuffer(buffer(buf),dtype=event_t)

            timestamp = dataHeader["st"]
            if not int(dataHeader["ts"]) == (pulseID+1):
                print "Lost pulse ",dataHeader["ts"]
            pulseID = int(dataHeader["ts"])
            self.count = self.count+1

            if time.time()-ctime > 10 :
                size = data.size*event_t.itemsize+sys.getsizeof(dataHeader)
                print "Received",self.count,"events (",size/1.e6,"MB) @ ",size*self.count/(10.*1e6)," MB/s"
                self.count = 0
                ctime = time.time()
        


def main(argv):
    fulladdress = argv[1]

    generatorReceiver(fulladdress)

#    context = zmq.Context()
#    readerSocket = context.socket(zmq.PULL)
#    readerSocket.connect(fulladdress)
#    count = 0
#    pulseID = 0
#
#    ctime=time.time()
#    while(True):
#
#        dataHeader = readerSocket.recv_json()
#        buf = readerSocket.recv(copy=True)
#        data = np.frombuffer(buffer(buf),dtype=event_t)
#
#        timestamp = dataHeader["st"]
#        if not int(dataHeader["ts"]) == (pulseID+1):
#            print "Lost pulse ",pulseID
#        pulseID = int(dataHeader["ts"])
#        count = count+1
#
#        if time.time()-ctime > 10 :
##            size = sys.getsizeof(dataHeader)
#            size = data.size*event_t.itemsize+sys.getsizeof(dataHeader)
#            print "Received",count,"events (",size/1.e6,"MB) @ ",size*count/(10.*1e6)," MB/s"
#            count = 0
#            ctime = time.time()


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print "Error, port required"
    main(sys.argv)
