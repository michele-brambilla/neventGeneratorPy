import time
import zmq
import sys
import numpy as np

from neventarray import *

def consumer(argv):
    port = argv[1]

    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:"+port)
    
#    data = np.empty(shape=0,dtype=eventDt)
    while(True):
        header = consumer_receiver.recv()
        buf = consumer_receiver.recv(copy=True)
        data = np.frombuffer(buffer(buf),dtype=eventDt)
        print header
        print data
#        data = work['num']
#        result = { 'consumer' : consumer_id, 'num' : data}

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print "Error, port required"
    consumer(sys.argv)
