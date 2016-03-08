import time
import zmq
import sys
import numpy as np
import json

from neventarray import *

def main(argv):
    fulladdress = argv[1]

    context = zmq.Context()
    readerSocket = context.socket(zmq.PULL)
    readerSocket.connect(fulladdress)
    count = 0
    pulseID = 0

    ctime=time.time()
    while(True):

        dataHeader = readerSocket.recv_json()
        buf = readerSocket.recv(copy=True)

        data = np.frombuffer(buffer(buf),dtype=eventDt)

        timestamp = dataHeader["st"]
        if not int(dataHeader["ts"]) == (pulseID+1):
            print "Lost pulse ",pulseID
        pulseID = int(dataHeader["ts"])
        count = count+1

        if time.time()-ctime > 10 :
            size = data.size*eventDt.itemsize+sys.getsizeof(dataHeader)
            print "Received",count,"events (",size/1.e6,"MB) @ ",size*count/(10.*1e6)," MB/s"
            count = 0
            ctime = time.time()


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print "Error, port required"
    main(sys.argv)
