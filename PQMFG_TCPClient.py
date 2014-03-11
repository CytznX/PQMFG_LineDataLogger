import socket
from threading import Thread
from StateMachineV2_0 import *
import thread

class ThreadedTCPNetworkAgent(Thread):
    
    '''Default constructor... Much Love''' 
    def __init__(self, ActivityLogger, portNum, BuffSize=1024):

        #Initialize myself as thread... =P
        Thread.__init__(self)

        self.CurLogger = ActivityLogger

        #setup some class variables
        self.running = True
        self._BuffSize = BuffSize
        self.Addr = ('', portNum)

        #create the socket that will be listening on
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind(self.Addr)
        self.serversock.listen(5)

    '''Heres where we spawn a minin thread that manages a individual connection to this machine'''
    def miniThread(self,clientsock,addr):
        while 1:
            data = clientsock.recv(self._BuffSize)
            
            #If theres nothing in the pipe... get out!!!
            if not data: 
                break
            elif "#END" == data.rstrip():
                break
            elif "#STATUS" == data.rstrip(): 
                for x in self.CurLogger.getFormatedLog():
                    clientsock.send(x)

        #close the damn thing from this side
        clientsock.close()

    def stop(self):
        #set runflag to False
        self.running = False

        #Create a connection to self so that we skip of blocking call
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self.Addr)

        #Kill the pipe
        self.serversock.close()

    def run(self):

        #All this loop does is listen for connections and spawn mini threads
        while self.running:

            #Here we wait for incoming connection
            clientsock, addr = self.serversock.accept()

            #we spawn new mini thread and pass off connection
            thread.start_new_thread(self.miniThread, (clientsock, addr))

if __name__=='__main__':
    a = ThreadedTCPNetworkAgent(None,5006)
    a.start() 