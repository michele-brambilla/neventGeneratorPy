import twisted
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory

from twisted.internet import reactor, defer, task, threads,protocol
import sys, signal, time

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver

class Echo(Protocol):
    def dataReceived(self, data):
        """As soon as any data is received, write it back."""
        print "Received : %s" % data
        self.transport.write(data)


class EchoFactory(ClientFactory) : 
    protocol = Echo

    def __init__ (self,prepend) :
        self.mes = prepend

    def dataReceived(self,data) :
        print prepend,data
        self.transport.write(data)


def main():
    f = Factory()
    f.protocol = Echo
    reactor.listenTCP(8000, f)
    reactor.run()

if __name__ == '__main__':
    main()
