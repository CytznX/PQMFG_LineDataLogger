#!/usr/bin/env python

import socket, os
import datetime, time
import openpyxl
import pickle

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
					Test = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self.CurrentLines[key])
					Test.send("#ALIVE")
					inData = Test.recv(self._BuffSize)
					if not inData:
						del(self.CurrentLines[key])

				except socket.error:
					del(self.CurrentLines[key])

				except TypeError:
					print "UHHHHHHH Typer error?", key, self.DefaultClientPort

			time.sleep(60)#Delay for 1 minute....


	'''Heres where we spawn a minin thread that manages a individual connection to this machine'''
	def miniThread(self,clientsock,addr):

		#Notify Connection made
		log = ['Connection Recieved@'+datetime.datetime.now().strftime('(%D, %H:%M:%S)')+' From Addr: '+str(addr)]

		#the collected message
		message = ''
		safety = ''
		data = ''
		#PULL IN NEW
		while True:
			data = clientsock.recv(self._BuffSize)
			if not data: break

			safety += data

		#(_machineVars, unPickledData[1], self._BatchInfo, self._PalletInfo, self._QCInfo, self.fillSheet)
		unPickledData = pickle.loads(safety)

		try:

			w0 = unPickledData[0]["WO"]

				if not os.path.isfile(self.WO_LogFolder+w0 +".xlsx"):

					#Create a new
					wb = Workbook()
					headerSheet = wb.active

					headerSheet.title = "Work Order Sumary"
					headerSheet['A1'] = "WO#: "
					headerSheet['B1'] = w0

					headerSheet['A1'].style.font.size = 20
					headerSheet['B1'].style.font.size = 20

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
					headerSheet['F3'] = "Total Fail"
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

					#1"Run#" 2"Start Time" 3"EndTime Time" 4"Total Count" 5"Total Box" 6"Total Tossed"

					headerSheet['A5'] = "1"
					headerSheet['B5'] = unPickledData[0]["WO StartTime"].strftime('(%D) @ %H:%M:%S')
					headerSheet['C5'] = unPickledData[0]["Time Log Created"].strftime('(%D) @ %H:%M:%S')
					headerSheet['D5'] = sum(unPickledData[0]["Total Count"])
					headerSheet['E5'] = sum(unPickledData[0]["Box Count"])
					headerSheet['F5'] = sum(unPickledData[0]["Fail Count"])

					FirstSheet = wb.create_sheet()
					FirstSheet.title = 'Run#1'

					_LastColumb = 1
					for key in unPickledData[0].keys():
						if not key == "Line Var Adjustments"
								and not key == "Maintanance Down Times"
								and not key == "Inventory Down Time"
								and not key == "Break Down Time":

						FirstSheet['A'+str(x)] = key
						FirstSheet['A'+str(x)].style.font.bold = True
						FirstSheet['B'+str(x)] = unPickledData[0][key]
						_LastColumb += 1
					_LastColumb += 1

					#get keys from working employee dictionary
					empKeys = unPickledData[1].keys()

					# temporrary storage arrays that help store all employees
					lineMechanics = ['----Mechanic(s)----']

					#heres the methodolagy for itterating over employee dictionary
					for key in empKeys:
						if(unPickledData[1][key][0]=="Line_Leader"):

							FirstSheet['A'+str(_LastColumb)] = '----Line Leader(s)----'
							FirstSheet['A'+str(_LastColumb)].style.font.bold = True
							_LastColumb += 1

							EmployOutputString = "" #key+": "
							WasActive = False
							for x,y in unPickledData[1][key][1]:
								if y == None:
									y = unPickledData[0]["Time Log Created"]

								if y > unPickledData[0]["WO StartTime"]:

									if not WasActive:
										EmployOutputString = key+": "
										WasActive = True
									EmployOutputString += ' ('+x.strftime('%H:%M:%S')+','+y.strftime('%H:%M:%S') +') '

							if WasActive:
								FirstSheet['A'+str(_LastColumb)] = EmployOutputString
								_LastColumb += 1

						elif(unPickledData[1][key][0]=="Line_Worker"):

							FirstSheet['A'+str(_LastColumb)] = '----Line Worker(s)----'
							FirstSheet['A'+str(_LastColumb)].style.font.bold = True
							_LastColumb += 1

							EmployOutputString = "" #key+": "
							WasActive = False
							for x,y in unPickledData[1][key][1]:
								if y == None:
									y =  unPickledData[0]["Time Log Created"]

								if y > self.WO_StartTime:
									if not WasActive:
										EmployOutputString = key+": "
										WasActive = True
									EmployOutputString += ' ('+x.strftime('%H:%M:%S')+','+y.strftime('%H:%M:%S') +') '

							if WasActive:
								FirstSheet['A'+str(_LastColumb)] = EmployOutputString
								_LastColumb += 1

						elif(unPickledData[1][key][0]=="Mechanic"):

							FirstSheet['A'+str(_LastColumb)] = '----Mechanic(s)----'
							FirstSheet['A'+str(_LastColumb)].style.font.bold = True
							_LastColumb += 1

							EmployOutputString = "" #key+": "
							WasActive = False
							for x,y in unPickledData[1][key][1]:
								if y == None:
									y =  unPickledData[0]["Time Log Created"]

								if y > self.WO_StartTime:
									if not WasActive:
										EmployOutputString = key+": "
										WasActive = True
									EmployOutputString += ' ('+x.strftime('%H:%M:%S')+','+y.strftime('%H:%M:%S') +') '
							if WasActive:
								FirstSheet['A'+str(_LastColumb)] = EmployOutputString
								_LastColumb += 1

					FirstSheet['A'+str(_LastColumb)] = '---Adjustments----'
					FirstSheet['A'+str(_LastColumb)].style.font.bold = True
					_LastColumb += 1

					for adjCounts in unPickledData[0]["Line Var Adjustments"]:
						FirstSheet['A'+str(_LastColumb)] = '('+str(adjCounts[0])+', '+str(adjCounts[1])+', '+str(adjCounts[2])+', '+adjCounts[3].strftime('%H:%M:%S')+')'
						_LastColumb += 1

					_LastColumb += 1
					FirstSheet['A'+str(_LastColumb)] = '---Down Time----'
					FirstSheet['A'+str(_LastColumb)].style.font.bold = True
					_LastColumb += 1

					maintainMsg = ""
					for start,end in self.MaintananceDwnTime:
						if not end == None:
							maintainMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
						else:
							maintainMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

					FirstSheet['A'+str(_LastColumb)] = 'Maintanance> '+str(FormattedMain[0])+':'+str(FormattedMain[1])+':'+str(FormattedMain[2])
					_LastColumb+=1
					FirstSheet['A'+str(_LastColumb)] = maintainMsg
					_LastColumb+=2

					InventoryMsg = []
					for start,end in self.InventoryDwnTime:
						if not end == None:
							InventoryMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) ']
						else:
							InventoryMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) ']

					QualityControlMsg = []
					for start,end in self.QualityControlDwnTime:
						if not end == None:
							QualityControlMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) ']
						else:
							QualityControlMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) ']

					breakMsg = []
					for start,end in self.BreakDownTime:
						if not end == None:
							breakMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) ']
						else:
							breakMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) ']

					log+=[]+[]+maintainMsg+[""]
					log+=['Inventory> '+str(FormattedInv[0])+':'+str(FormattedInv[1])+':'+str(FormattedInv[2])]+InventoryMsg+[""]
					log+=['Quality_Control> '+str(FormattedQuality[0])+':'+str(FormattedQuality[1])+':'+str(FormattedQuality[2])]+QualityControlMsg+[""]
					log+=['Break> '+str(FormattedBreak[0])+':'+str(FormattedBreak[1])+':'+str(FormattedBreak[2])]+breakMsg+[""]
					log+=['Total> '+str(FormattedTotal[0])+':'+str(FormattedTotal[1])+':'+str(FormattedTotal[2])]

		except IndexError, e:
			pass



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