import socket
from threading import Thread
from StateMachine import *
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
			command = data.split()
			#If theres nothing in the pipe... get out!!!

			if len(command)>1:
				if command[0] == "#UP" and len(command) == 2:
					self.CurLogger.changeState(command[1])
					clientsock.send("AKN\n")

				elif command[0] == "#DOWN" and len(command) == 3:
					#current possible reasons: 1)Maitenance, 2) Inventory, 3) Quality_Control
					self.CurLogger.changeState(command[2], command[1])
					clientsock.send("AKN\n")

				elif command[0] == "#ADD":
					for x in range(1,len(command)):
						self.CurLogger.addEmployee(command[x]) 
					clientsock.send("AKN\n")

				elif command[0] == "#REMOVE":
					for x in range(1,len(command)):
						self.CurLogger.removeEmployee(command[x]) 
					clientsock.send("AKN\n")

				elif command[0] == "#SETPPB" and len(command) == 2:
					self.CurLogger.changePeacesPerBox(int(command[1]))
					clientsock.send("AKN\n")

				elif command[0] == "#ADJUST" and len(command) == 4:
					if command[1] == "TOTAL":
						self.CurLogger.inc_CurTotalCount(None, int(command[2]), True, command[3])
					elif command[1] == "BOX":
						self.CurLogger.inc_CurBoxCount(None, int(command[2]), True, command[3])
					clientsock.send("AKN\n")

				elif command[0] == "#CHANGE" and len(command) == 2:
					self.CurLogger.changeCurrentWO(command[1], False)
					clientsock.send("AKN\n")

				elif command[0] == "#MSG" and self.isInt(command[-1]):
					msg = ''
					for y in range(1, len(command)-1):
						msg += command[y]+" "

					self.CurLogger.pushMessage(msg, command[-1])
					clientsock.send("AKN\n")

			else:
				if not data: 
					break
				elif "#END" == data.rstrip():
					break
				elif "#STATUS" == data.rstrip(): 
					for x in self.CurLogger.getFormatedLog():
						clientsock.send(x+"\n")
				elif "#ALIVE" == data.rstrip():
					clientsock.send(str(self.CurLogger.getCurrentState()))
				elif "#COMPLETE" == data.rstrip():
					self.CurLogger.finishCurrentWO()
					clientsock.send("AKN\n")
				else:
					clientsock.send("INVALID COMMAND\n")

		#close the damn pipe from this side
		clientsock.close()

	def stop(self):
		#set runflag to False
		self.running = False

		#Create a connection to self so that we skip of blocking call
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self.Addr)

		#Kill the pipe
		self.serversock.close()

	def isInt(self,x):
		try:
			int(x)
			return True
		except ValueError,e:
			return False

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