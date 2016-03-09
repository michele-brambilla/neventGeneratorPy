from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

import threading

import time


class Gen(LineReceiver):

    def __init__(self):
        self.status = False
        
    def connectionMade(self):
        self.sendLine("Type run to start counter")
        self.sendLine("Type pause to stop counter")
        
    def connectionLost(self, reason):
        print "Disconnetting controller"
        
    def lineReceived(self, line):
        if line == "run" :
            self.status = True
            self.factory.run()
        if line == "pause" :
            self.status = False
            self.factory.pause()
        self.sendLine(str(self.factory.val))
            
class GenFactory(Factory):

    protocol = Gen
    
    def __init__(self, status=False,sleeptime=1):
        self.status = status
        self.sleeptime = sleeptime
        self.val = 0

    def run(self) :
        if (self.status == False) :
            print "started counting"
            self.status = True
            thread = threading.Thread(target=self.startCounting)
            thread.daemon = True
            thread.start()
        else :
            print "Nothing to do, I'm already counting!"
            
    def pause(self) :
        if (self.status == True) :
            print "paused counting"
            self.status = False
        else :
            print "Nothing to do, I'm already in pause!"

    def startCounting(self):
        while ( self.status == True ) :
            self.val += 1
            print self.status,self.val
            time.sleep (self.sleeptime)

            
reactor.listenTCP(8123, GenFactory(status=False))
reactor.run()
