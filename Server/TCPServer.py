#!/usr/bin/env python

import socket, os
import datetime, time

from threading import Thread
from openpyxl import *

class ThreadedTCPNetworkAgent(Thread):
	
	'''Default constructor... Much Love''' 
	def __init__(self, portNum, Folder= 'WorkOrderExcelLogs',BuffSize=1024):

		#Initialize myself as thread... =P
		Thread.__init__(self)

		#setup some class variables
		self.running = True
		self.DefaultClientPort= 5005
		self._BuffSize = BuffSize
		self.Addr = ('', portNum)

		self.CurrentLines = dict()

		self.IsMachineAlive = Thread(target=self.whoIsAlive, args=())
		self.IsMachineAlive.start()
		
		#FOR TESTING ONLY
		self.testing = True
		'''if self.testing:
			self.CurrentLines[3] =("192.168.20.198", 5005)
			self.CurrentLines[4] =("192.168.20.198", 5005)
			self.CurrentLines[5] =("192.168.20.198", 5005)
			self.CurrentLines[11] =("192.168.20.198", 5005)			  
			self.CurrentLines[34] =("192.168.20.198", 5005)
			self.CurrentLines[7] =("192.168.20.198", 5005)
		'''
		
		#Creates the logg folder if it doesnt exist
		self.WO_LogFolder = Folder+'/'
		if not os.path.isdir(self.WO_LogFolder):
			os.makedirs(self.WO_LogFolder)

		#create the socket that will be listening on
		self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversock.bind(self.Addr)
		self.serversock.listen(5)

	def whoIsAlive(self):
		while self.running:
			for key in self.CurrentLines.keys():

				try: 
					Test = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((key, self.DefaultClientPort))
					Test.send("#ALIVE")
					inData = Test.recv(self._BuffSize)
					if not inData:
						del(self.CurrentLines[key])

				except Error:
					del(self.CurrentLines[key])

			time.sleep(60)#Delay for 1 minute....


	'''Heres where we spawn a minin thread that manages a individual connection to this machine'''
	def miniThread(self,clientsock,addr):
		
		#Notify Connection made
		log = ['Connection Recieved@'+datetime.datetime.now().strftime('(%D, %H:%M:%S)')+' From Addr: '+str(addr)]

		#the collected message
		message = ''
		safety = ''

		#PULL IN NEW 
		while self.running:
			data = clientsock.recv(self._BuffSize)
			safety += data
			if self.testing: print "From "+str(addr)+": ", data, safety

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

			elif data.rstrip().startswith('#GET_ACTIVE') or safety.rstrip().startswith('#GET_ACTIVE'):
				if not self.CurrentLines.keys() == []:
					for key in self.CurrentLines.keys():
						msg = "Line: "+str(key)+" " +str(self.CurrentLines[key])+"\n"
						clientsock.send(msg)
						if self.testing: print msg
				else:
						clientsock.send("#NONE")

				break

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

					if os.path.isfile(w0 +".xlsx"):
						wb = Workbook()
						headerSheet = wb.active
						headerSheet.title = "Work Order Sumary"
						headerSheet['A1'] = "WO#: "
						headerSheet['B1'] = w0
						headerSheet['A3'] = "Run#"
						headerSheet['B3'] = "Start Time"
						headerSheet['c3'] = "EndTime Time"
					else:


					formattedMess[0] = 'W/O#: '+ formattedMess[0]
					formattedMess[1] = 'Line#: '+ formattedMess[1]
					formattedMess[2] = 'Start Time: '+ formattedMess[2]
					formattedMess[3] = 'Status/RunTime: '+ formattedMess[3]+'(seconds)'
					formattedMess[4] = 'Total Count: '+ formattedMess[4]
					formattedMess[5] = 'Total Hourly: '+ formattedMess[5]
					formattedMess[6] = 'Box Count: '+ formattedMess[6]
					formattedMess[7] = 'Box Hourly: '+ formattedMess[7]
					formattedMess[8] = 'Fail Count: '+ formattedMess[8]

					if formattedMess[9] == '':
						formattedMess[9] = 'Peaces Per Box: N/A'
					else:
						formattedMess[9] = 'Peaces Per Box: '+ formattedMess[9]

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

		if self.testing: print "Setting RunFlag to False"
		self.running = False

		if self.testing: print "Waiting for alive thread to join"
		self.IsMachineAlive.join()

		#Create a connection to self so that we skip of blocking call
		if self.testing: print "Creating Kill Connection"
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self.Addr)

		#Kill the pipe
		if self.testing: print "Clossing Pipe"
		self.serversock.close()


	def run(self):

		#All this loop does is listen for connections and spawn mini threads
		while self.running:

			#Here we wait for incoming connection
			clientsock, addr = self.serversock.accept()
			if self.testing: print "Connection Started: ", addr
			#we spawn new mini thread and pass off connection
			Thread(target=self.miniThread, args=(clientsock, addr)).start()

if __name__=='__main__':
	a = ThreadedTCPNetworkAgent(5006)
	a.start()