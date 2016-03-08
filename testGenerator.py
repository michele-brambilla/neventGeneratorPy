from nexus2event import *
from neventarray import *

import sys
import os
import errno
import numpy
import time

import zmq
import twisted

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol, ClientFactory


def usage() :
    print ""
    print "Usage:"
    print "\tpython "+sys.argv[0]+" <nexus file> <port> (<multiplier>)"
    print ""
    sys.exit(-1)


class generatorFake(Protocol):
    def doStart(self):
        pass

    def startedConnecting(self, connectorInstance):
        print connectorInstance

    def buildProtocol(self, address):
        print address
        return self.protocol()
         
    def clientConnectionLost(self, connection, reason):
        print reason
        print connection
         
    def clientConnectionFailed(self, connection, reason):
        print connection
        print reason

    def doStop(self):
        pass

    def dataReceived(self,data) :
        self.transport.write(data)
        if self.pause == False and data == "pause":
            self.pause = True
            print "Generator paused"
        if self.pause == True and data == "run":
            self.pause = False

class generatorFakeFactory(ClientFactory):
    protocol = generatorFake

    def __init__ (self,msg) :
        print msg
    
    def doStart(self):
        pass

#    def buildProtocol(self, addr):
#        print 'Connected.'
#        return generatorFake()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason




class generatorSource(LineReceiver):

    def __init__ (self,source,port,multiplier,mock=False):
        self.source = source
        self.port = port
        self.multiplier = multiplier
# LineReceiver
        self.pause = True
        self.isCounting  = False

        self.context = zmq.Context()
        self.data = self.load(mock)
        self.socket = self.connect()
        self.count = 0
#        self.run()


    def lineReceived(self,data) :
        self.transport.write(data)
        if self.pause == False and data == "pause":
            self.pause = True
            print "Generator paused"
            if self.pause == True and data == "run":
                self.pause = False
                print "Generator is running"
                
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


    control_port = 33757


    reactor.connectTCP("127.0.0.1", control_port, generatorFake())
#    reactor.connectTCP("pc11997", control_port, generatorFakeFactory("parametri"))
#
#    f = Factory()
##    factory.protocol = generatorSource(source,port,multiplier,mock=True)
#    f.protocol = generatorFakeFactory
#    reactor.listenTCP(control_port, f)
    reactor.run()

#    generatorSource(source,port,multiplier,mock=True)
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
    main(sys.argv)




