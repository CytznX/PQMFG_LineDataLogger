#!/usr/bin/env python

import socket, os
import datetime, time
import openpyxl

from threading import Thread
from openpyxl import Workbook
from openpyxl import load_workbook

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
			if self.testing: print "From "+str(addr)

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

				if not os.path.isfile(self.WO_LogFolder+w0 +".xlsx"):
					
					#Create a new 
					wb = Workbook()
					headerSheet = wb.active
					

					headerSheet.title = "Work Order Sumary"
					headerSheet['A1'] = "WO#: "
					headerSheet['B1'] = w0

					#Creates Headers For Data Columbs
					headerSheet['A3'] = "Run#"
					headerSheet['A3'].style.font.bold = True
					headerSheet['B3'] = "Start Time"
					headerSheet['B3'].style.font.bold = True
					headerSheet['C3'] = "EndTime Time"
					headerSheet['C3'].style.font.bold = True
					headerSheet['D3'] = "Total Count"
					headerSheet['D3'].style.font.bold = True
					headerSheet['E3'] = "Total Box"
					headerSheet['E3'].style.font.bold = True
					headerSheet['F3'] = "Total Tossed"
					headerSheet['F3'].style.font.bold = True

					headerSheet['A4'] = "------------"
					headerSheet['A4'].style.font.bold = True
					headerSheet['B4'] = "------------"
					headerSheet['B4'].style.font.bold = True
					headerSheet['C4'] = "------------"
					headerSheet['C4'].style.font.bold = True
					headerSheet['D4'] = "------------"
					headerSheet['D4'].style.font.bold = True
					headerSheet['E4'] = "------------"
					headerSheet['E4'].style.font.bold = True
					headerSheet['F4'] = "------------"
					headerSheet['F4'].style.font.bold = True

					headerSheet['A5'] = "1"
					headerSheet['B5'] = formattedMess[2]
					headerSheet['C5'] = formattedMess[3].split()[1]
					headerSheet['D5'] = formattedMess[4]
					headerSheet['E5'] = formattedMess[6]
					headerSheet['F5'] = formattedMess[8]

					FirstSheet = wb.create_sheet()
					FirstSheet.title = 'Run#1'

					#Second
					FirstSheet['A1'] = 'Line#: '
					FirstSheet['A1'].style.font.bold = True
					FirstSheet['B1'] = formattedMess[1]

					#Third
					FirstSheet['A2'] = 'Start Time: '
					FirstSheet['A2'].style.font.bold = True
					FirstSheet['B2'] = formattedMess[2]

					#Forth
					FirstSheet['A3'] = formattedMess[3].split()[0]
					FirstSheet['A3'].style.font.bold = True
					FirstSheet['B3'] = formattedMess[3].split()[1]

					#Five
					FirstSheet['A4'] = 'Total Count: '
					FirstSheet['A4'].style.font.bold = True
					FirstSheet['B4'] = formattedMess[4]

					#Six
					FirstSheet['A5']= 'Total Hourly: '
					FirstSheet['A5'].style.font.bold = True
					FirstSheet['B5']= formattedMess[5]						

					#Seven
					FirstSheet['A6']= 'Box Count: '
					FirstSheet['A6'].style.font.bold = True
					FirstSheet['B6']= formattedMess[6] 
					
					#Eight
					FirstSheet['A7']= 'Box Hourly: '
					FirstSheet['A7'].style.font.bold = True
					FirstSheet['B7']= formattedMess[7] 
					
					#Nine
					FirstSheet['A8']= 'Fail Count: '
					FirstSheet['A8'].style.font.bold = True 
					FirstSheet['B8']= formattedMess[8] 

					if formattedMess[9] == '':
						FirstSheet['A9'] = 'Peaces Per Box: ' 
						FirstSheet['B9'] = 'N/A' 
					else:
						FirstSheet['A9'] = 'Peaces Per Box: ' 
						FirstSheet['B9'] = formattedMess[9]
					
					FirstSheet['A9'].style.font.bold = True

					for count in range(10,len(formattedMess)):
						FirstSheet['A'+str(count)]=formattedMess[count]

					wb.save(self.WO_LogFolder+w0+".xlsx")#<<<<<<<<<<<<<<<<<<<<-------------------------------------------- Save the file

				else:

					wb = load_workbook(self.WO_LogFolder+w0+'.xlsx')

					headerSheet = wb.get_sheet_by_name("Work Order Sumary")
					SheetNames = wb.get_sheet_names()

					print len(SheetNames)

					headerSheet['A'+str(4+len(SheetNames))] = str(len(SheetNames))
					headerSheet['B'+str(4+len(SheetNames))] = formattedMess[2]
					headerSheet['C'+str(4+len(SheetNames))] = formattedMess[3].split()[1]
					headerSheet['D'+str(4+len(SheetNames))] = formattedMess[4]
					headerSheet['E'+str(4+len(SheetNames))] = formattedMess[6]
					headerSheet['F'+str(4+len(SheetNames))] = formattedMess[8]

					NewSheet = wb.create_sheet()
					NewSheet.title = 'Run#'+str(len(SheetNames))

					#Second
					NewSheet['A1'] = 'Line#: '
					NewSheet['A1'].style.font.bold = True
					NewSheet['B1'] = formattedMess[1]

					#Third
					NewSheet['A2'] = 'Start Time: '
					NewSheet['A2'].style.font.bold = True
					NewSheet['B2'] = formattedMess[2]

					#Forth
					NewSheet['A3'] = formattedMess[3].split()[0]
					NewSheet['A3'].style.font.bold = True
					NewSheet['B3'] = formattedMess[3].split()[1]

					#Five
					NewSheet['A4'] = 'Total Count: '
					NewSheet['A4'].style.font.bold = True
					NewSheet['B4'] = formattedMess[4]

					#Six
					NewSheet['A5']= 'Total Hourly: '
					NewSheet['A5'].style.font.bold = True
					NewSheet['B5']= formattedMess[5]						

					#Seven
					NewSheet['A6']= 'Box Count: '
					NewSheet['A6'].style.font.bold = True
					NewSheet['B6']= formattedMess[6] 
					
					#Eight
					NewSheet['A7']= 'Box Hourly: '
					NewSheet['A7'].style.font.bold = True
					NewSheet['B7']= formattedMess[7] 
					
					#Nine
					NewSheet['A8']= 'Fail Count: '
					NewSheet['A8'].style.font.bold = True 
					NewSheet['B8']= formattedMess[8] 

					if formattedMess[9] == '':
						NewSheet['A9'] = 'Peaces Per Box: ' 
						NewSheet['B9'] = 'N/A' 
					else:
						NewSheet['A9'] = 'Peaces Per Box: ' 
						NewSheet['B9'] = formattedMess[9]
					
					NewSheet['A9'].style.font.bold = True
					
					for count in range(10,len(formattedMess)):
						NewSheet['A'+str(count)]=formattedMess[count]


					wb.save(self.WO_LogFolder+w0+".xlsx")#<<<<<<<<<<<<<<<<<<<<-------------------------------------------- Save the file

				fullPath = self.WO_LogFolder + w0+'.xlsx'					
				log += ['Log Created: '+fullPath]

			except IndexError, e:
				log += ['Data Is bad']

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