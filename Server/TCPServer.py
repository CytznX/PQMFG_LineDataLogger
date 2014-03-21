#!/usr/bin/env python

import socket, os
from threading import Thread
import thread
import datetime

class ThreadedTCPNetworkAgent(Thread):
	
	'''Default constructor... Much Love''' 
	def __init__(self, portNum, Folder= 'WorkOrderLogs',BuffSize=1024):

		#Initialize myself as thread... =P
		Thread.__init__(self)

		#setup some class variables
		self.running = True
		self._BuffSize = BuffSize
		self.Addr = ('', portNum)

		self.CurrentLines = dict()
		
		#Creates the logg folder if it doesnt exist
		self.WO_LogFolder = Folder+'/'
		if not os.path.isdir(self.WO_LogFolder):
			os.makedirs(self.WO_LogFolder)

		#create the socket that will be listening on
		self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversock.bind(self.Addr)
		self.serversock.listen(5)

	'''Heres where we spawn a minin thread that manages a individual connection to this machine'''
	def miniThread(self,clientsock,addr):
		
		#Notify Connection made
		log = ['Connection Recieved@'+datetime.datetime.now().strftime('(%D, %H:%M:%S)')+' From Addr: '+str(addr)]

		#the collected message
		message = ''
		
		#PULL IN NEW 
		while 1:
			data = clientsock.recv(self._BuffSize)
			
			#If theres nothing in the pipe... get out!!!
			if not data: 
				break
			elif data.rstrip().startswith('#CONNECT') and len(data.rstrip().split())== 2:
				cmd = data.rstrip().split()
				self.CurrentLines[int(cmd[1])] = addr

			elif data.rstrip().startswith('#SHUTTING_DOWN'):
				for key in self.CurrentLines.keys():
					if self.CurrentLines[key][0] == addr[0]:
						del(self.CurrentLines[key])

			elif data.rstrip().startswith('#GET_ACTIVE'):
				for key in self.CurrentLines.keys():
					clientsock.send("Line: "+str(key)+" " +str(self.CurrentLines[key]))

			elif "#END" == data.rstrip(): 
				self.stop()
				break # type '#END' on client console to close connection from the server side
			elif not data.rstrip().startswith('#'):
				message += data


		formattedMess = message.split('////')

		#close the damn thing from this side
		clientsock.close()

		if not data.rstrip().startswith('#') and not message == '':
			#CREATE XLSX DOC
			#--------------------------------------------------------------
			try:

				w0 = formattedMess[0]
				formattedMess[0] = 'W/O#: '+ formattedMess[0]
				formattedMess[1] = 'Line#: '+ formattedMess[1]
				formattedMess[2] = 'Start Time: '+ formattedMess[2]
				formattedMess[3] = 'EndTime: '+ formattedMess[3]
				formattedMess[4] = 'Total Count: '+ formattedMess[4]
				formattedMess[5] = 'Fail Count: '+ formattedMess[5]
				formattedMess[6] = 'Box Count: '+ formattedMess[6]

				if formattedMess[7] == '':
					formattedMess[7] = 'Peaces Per Box: N/A'
				else:
					formattedMess[7] = 'Peaces Per Box: '+ formattedMess[7]

				if not os.path.isdir(self.WO_LogFolder + w0+'/'):
					os.makedirs(self.WO_LogFolder + w0+'/')

				count = 1
				while os.path.exists(self.WO_LogFolder + w0+'/Run#'+str(count)+'.txt'): 
					count += 1

				fullPath = self.WO_LogFolder + w0+'/Run#'+str(count)+'.txt'
				self.writeFile(fullPath,formattedMess)
				
				log += ['Log Created: '+fullPath]

			except IndexError, e:
				log += ['Data Is bad']

			log += ['-------------------------END-------------------------']

		else:
			log += ['MACHINE IS GOING DOWN DO TO EXTERNAL COMAND']
			log += ['-------------------------END-------------------------']

		self.writeFile('ServerConLogFile.txt', log, "a")
			
	def writeFile(self, FileName, Content , write ="w"):
		myfile = open(FileName, write)
		for newLine in Content:
			myfile.write(newLine+'\n')
		myfile.close()

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
			print "someones talking: ", addr
			#we spawn new mini thread and pass off connection
			thread.start_new_thread(self.miniThread, (clientsock, addr))

if __name__=='__main__':
	a = ThreadedTCPNetworkAgent(5006)
	a.start()