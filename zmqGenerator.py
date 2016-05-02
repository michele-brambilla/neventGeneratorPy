from nexus2event import *
from neventarray import *

import sys, os, getopt
import errno
import numpy
import time

import zmq
import twisted
from twisted.internet.defer import inlineCallbacks


def usage() :
    print ""
    print "Usage:"
    print "\tpython",sys.argv[0],"[-h -m -r] <nexus file> <port> (<multiplier>)"
    print ""
    print "-h: this help"
    print "-m: use fake data"
    print ""



class generatorSource:

    def __init__ (self,source,port,multiplier,debug_data=False,mock=False):
        self.source = source
        self.port = port
        self.multiplier = multiplier
        self.do_debug = debug_data
        self.context = zmq.Context()
        self.data = self.load(mock)
        self.socket = self.connect()
        self.count = 0
        self.run()


    def histo(self,data):
        hist,bin_edge = np.histogram(data["x"], bins=np.arange(129))
        for i in np.arange(128):
            print 0,bin_edge[i],hist[i]
        hist,bin_edge = np.histogram(data["y"], bins=np.arange(129))
        for i in np.arange(128):
            print 1,bin_edge[i],hist[i]


    def load(self,mock):
        data = loadNeXus2event(self.source)
            
        if self.multiplier > 1:
            data = multiplyNEventArray(data,int(self.multiplier))

        return data

    def connect(self):
        zmq_socket = self.context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://*:"+self.port)
        zmq_socket.setsockopt(zmq.SNDHWM, 100)
        return zmq_socket


    def mutation(self,d):

        o = d
        if  np.random.rand() > .999 :
            o = np.delete(o,np.random.rand(o.size))
            print "Error: missing value"
        if  0.998 < np.random.rand() <= .999 :
            x = np.random.randint(o.size)
            o[x]["ts"] = 2<<32
            print "Error: wrong timestamp"
        if  0.997 < np.random.rand() <= .998 :
            x = np.random.randint(o.size)
            o[x]["sync"] = 1
            print o[x]
            print "Error: sync"

        return o
    
    def run(self):
        data = self.data
        ctime=time.time()
        pulseID=0

        stream_frequency = 1./14.
        if self.do_debug:
            stream_frequency = 0.5

        print sys.getsizeof(self.data)
        print self.data.size*self.data.dtype.itemsize/(1024.*1024.),"MB"

        while(True):
            itime = time.time()
            dataHeader=header(pulseID,itime,12345678,self.data.shape[0])

            def send_data(socket,head):
                socket.send_json(head)
                socket.send(self.data)
#                socket.send(self.mutation(self.data))
                self.count += 1
                
            send_data(self.socket,dataHeader)

            elapsed = time.time() - itime
            remaining = stream_frequency-elapsed

            if remaining > 0:
                time.sleep (remaining)

            pulseID += 1

            if time.time()-ctime > 10 :
                size = (self.data.size*self.data.dtype.itemsize+
                        sys.getsizeof(dataHeader))

                print "Sent ",self.count," events @ ",size*self.count/(10.*1e6)," MB/s"
                self.count = 0
                ctime = time.time()







def main(argv,debug=False,mock=False):

    source = argv[0]
    port = argv[1]

    multiplier = 1
    if len(argv) > 2:
        multiplier = argv[2]

    generatorSource(source,port,multiplier,debug,mock)
    


if __name__ == "__main__":
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hdm",["help","debug","mock"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    if len(args) < 2:
        usage()
        exit(2)
    
    mock = False
    debug = False
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
            sys.exit()
        if o in ("-m","--mock"):
            mock = True
        if o in ("-d","--debug"):
            debug = True

    main(args,debug,mock)
