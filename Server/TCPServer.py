#!/usr/bin/env python

import socket, os
import datetime, time
import pickle

from threading import Thread
from openpyxl import *
from openpyxl.styles import *

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
		#print 'Connection Recieved@'+datetime.datetime.now().strftime('(%D, %H:%M:%S)')+' From Addr: '+str(addr)

		#the collected message
		safety = ''
		data = ''
		#PULL IN NEW
		while True:
			data = clientsock.recv(self._BuffSize)
			if not data: break

			safety += data

		try:

			#(_machineVars, unPickledData[1], self._BatchInfo, self._PalletInfo, self._QCInfo, self.fillSheet)
			unPickledData = pickle.loads(safety)

			w0 = unPickledData[0]["WO"]

			if not os.path.isfile(self.WO_LogFolder+w0 +".xlsx"):

				#Create a new
				wb = Workbook()
				headerSheet = wb.active

				headerSheet.title = "Work Order Sumary"
				headerSheet['A1'] = "WO#: "
				headerSheet['B1'] = w0

				headerSheet.set_style('A1', styles.Style(font=Font(size=20, bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_RIGHT)))
				headerSheet.set_style('B1', styles.Style(font=Font(size=20, bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_LEFT)))

				#Creates Headers For Data Columbs
				headerSheet['A3'] = "Run#"
				headerSheet.set_style('A3', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['B3'] = "Start Time"
				headerSheet.set_style('B3', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['C3'] = "EndTime Time"
				headerSheet.set_style('C3', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['D3'] = "Total Count"
				headerSheet.set_style('D3', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['E3'] = "Total Box"
				headerSheet.set_style('E3', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['F3'] = "Total Fail"
				headerSheet.set_style('F3', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				headerSheet['A4'] = "------------"
				headerSheet.set_style('A4', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['B4'] = "------------"
				headerSheet.set_style('B4', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['C4'] = "------------"
				headerSheet.set_style('C4', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['D4'] = "------------"
				headerSheet.set_style('D4', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['E4'] = "------------"
				headerSheet.set_style('E4', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
				headerSheet['F4'] = "------------"
				headerSheet.set_style('F4', styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				#1"Run#" 2"Start Time" 3"EndTime Time" 4"Total Count" 5"Total Box" 6"Total Tossed"

				headerSheet['A5'] = "1"
				headerSheet.set_style('A5', styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				headerSheet['B5'] = unPickledData[0]["WO StartTime"].strftime('(%D) @ %H:%M:%S')
				headerSheet.set_style('B5', styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				headerSheet['C5'] = unPickledData[0]["Time Log Created"].strftime('(%D) @ %H:%M:%S')
				headerSheet.set_style('C5', styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				headerSheet['D5'] = sum(unPickledData[0]["Total Count"])
				headerSheet.set_style('D5', styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				headerSheet['E5'] = sum(unPickledData[0]["Box Count"])
				headerSheet.set_style('E5', styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				headerSheet['F5'] = unPickledData[0]["Fail Count"]
				headerSheet.set_style('F5', styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

				FirstSheet = wb.create_sheet()
				FirstSheet.title = 'Run#1'


				_preOrderedKeys = ["Machine ID", "WO", "WO StartTime", "Time Log Created", "Total Count", "Fail Count", "Box Count", "Peaces Per Box", "Fill Start", "Fill End"]

				_LastColumb = 1
				for key in _preOrderedKeys:
					if not key == "Line Var Adjustments" and not key == "Maintanance Down Times" and not key == "Inventory Down Time" and not key == "Break Down Time":

						FirstSheet['A'+str(_LastColumb)] = key
						FirstSheet.set_style('A'+str(_LastColumb), styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_LEFT)))

						try:
							FirstSheet['B'+str(_LastColumb)] = unPickledData[0][key]
							FirstSheet.set_style('B'+str(_LastColumb), styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))

						except ValueError, e:

							FirstSheet['B'+str(_LastColumb)] = sum(unPickledData[0][key])
							FirstSheet.set_style('B'+str(_LastColumb), styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
							_LastColumb += 1

							FirstSheet['A'+str(_LastColumb)] = "^^^Hrly"
							FirstSheet.set_style('A'+str(_LastColumb), styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_LEFT)))

							FirstSheet['B'+str(_LastColumb)] = str(unPickledData[0][key])
							FirstSheet.set_style('B'+str(_LastColumb), styles.Style(alignment=Alignment(horizontal=alignment.HORIZONTAL_CENTER)))
							_LastColumb += 1

						_LastColumb += 1
				_LastColumb += 1

				#get keys from working employee dictionary
				empKeys = unPickledData[1].keys()
				_Postitions = ["Line_Leader", "Line_Worker", "Mechanic"]

				#heres the methodolagy for itterating over employee dictionary
				for pos in _Postitions:

					FirstSheet['A'+str(_LastColumb)] = '----'+pos+'(s)----'
					FirstSheet   .set_style('A'+str(_LastColumb), styles.Style(font=Font(bold=True), alignment=Alignment(horizontal=alignment.HORIZONTAL_RIGHT)))
					_LastColumb += 1

					for key in empKeys:
						if(unPickledData[1][key][0]==pos):

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

					_LastColumb += 1

				_LastColumb += 1
				FirstSheet['A'+str(_LastColumb)] = '---Adjustments----'
				headerSheet.set_style('A'+str(_LastColumb), styles.Style(font=Font(bold=True)))
				_LastColumb += 1

				for adjCounts in unPickledData[0]["Line Var Adjustments"]:
					FirstSheet['A'+str(_LastColumb)] = '('+str(adjCounts[0])+', '+str(adjCounts[1])+', '+str(adjCounts[2])+', '+adjCounts[3].strftime('%H:%M:%S')+')'
					_LastColumb += 1

				_LastColumb += 1
				FirstSheet['A'+str(_LastColumb)] = '---Down Time----'
				headerSheet.set_style('A'+str(_LastColumb), styles.Style(font=Font(bold=True)))
				_LastColumb += 1

				maintainMsg = ""
				for start,end in unPickledData[0]["Maintanance Down Times"]:
					if not end == None:
						maintainMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						maintainMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

				FirstSheet['A'+str(_LastColumb)] = 'Maintanance> '+str(unPickledData[2]["FormattedMain"][0])+':'+str(unPickledData[2]["FormattedMain"][1])+':'+str(unPickledData[2]["FormattedMain"][2])
				_LastColumb+=1
				FirstSheet['A'+str(_LastColumb)] = maintainMsg
				_LastColumb+=2

				InventoryMsg = ""
				for start,end in unPickledData[0]["Inventory Down Time"]:
					if not end == None:
						InventoryMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						InventoryMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

				FirstSheet['A'+str(_LastColumb)] = 'Inventory> '+str(unPickledData[2]["FormattedInv"][0])+':'+str(unPickledData[2]["FormattedInv"][1])+':'+str(unPickledData[2]["FormattedInv"][2])
				_LastColumb+=1
				FirstSheet['A'+str(_LastColumb)] = InventoryMsg
				_LastColumb+=2

				QualityControlMsg = ""
				for start,end in unPickledData[0]["Quality Control Down Time"]:
					if not end == None:
						QualityControlMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						QualityControlMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

				FirstSheet['A'+str(_LastColumb)] = 'Quality_Control> '+str(unPickledData[2]["FormattedQuality"][0])+':'+str(unPickledData[2]["FormattedQuality"][1])+':'+str(unPickledData[2]["FormattedQuality"][2])
				_LastColumb+=1
				FirstSheet['A'+str(_LastColumb)] = InventoryMsg
				_LastColumb+=2

				breakMsg = []
				for start,end in unPickledData[0]["Break Down Time"]:
					if not end == None:
						breakMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) ']
					else:
						breakMsg += ['(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) ']

				FirstSheet['A'+str(_LastColumb)] = 'Break> '+str(unPickledData[2]["FormattedBreak"][0])+':'+str(unPickledData[2]["FormattedBreak"][1])+':'+str(unPickledData[2]["FormattedBreak"][2])
				_LastColumb+=1
				FirstSheet['A'+str(_LastColumb)] = InventoryMsg
				_LastColumb+=2

				FirstSheet['A'+str(_LastColumb)] = 'Total> '+str(unPickledData[2]["FormattedTotal"][0])+':'+str(unPickledData[2]["FormattedTotal"][1])+':'+str(unPickledData[2]["FormattedTotal"][2])
				headerSheet.set_style('A'+str(_LastColumb), styles.Style(font=Font(bold=True)))
				_LastColumb+=2

				headerSheet.column_dimensions["A"].width = 15.0
				headerSheet.column_dimensions["B"].width = 30.0
				headerSheet.column_dimensions["C"].width = 30.0
				headerSheet.column_dimensions["D"].width = 15.0
				headerSheet.column_dimensions["E"].width = 15.0
				headerSheet.column_dimensions["F"].width = 15.0

				headerSheet.row_dimensions[1].height = 40

				FirstSheet.column_dimensions["A"].width = 30.0
				FirstSheet.column_dimensions["B"].width = 30.0

				FirstFillSheet = wb.create_sheet()
				FirstFillSheet.title = 'FillSheet#1'


				FirstFillSheet['A1'] = "WO#: "
				FirstFillSheet['B1'] = w0
				FirstFillSheet['C1'] = "Fill SHEET "
				FirstFillSheet.row_dimensions[1].height = 40

				FirstFillSheet.set_style('A1', styles.Style(font=Font(size=20, bold=True, )))
				FirstFillSheet.set_style('B1', styles.Style(font=Font(size=20, bold=True, )))
				FirstFillSheet.set_style('C1', styles.Style(font=Font(size=20, bold=True, )))

				_counter=2
				for fillSheetItems in unPickledData[3].keys():
					FirstFillSheet['A'+str(_counter)] = fillSheetItems
					FirstFillSheet['B'+str(_counter)] = unPickledData[3][fillSheetItems]
					FirstFillSheet.set_style('A'+str(_counter), styles.Style(font=Font(size=20, bold=True, )))
					_counter+=1
				_counter+=1

				_RowLetter = "A"
				for batchHeaders in unPickledData[4]["INIT"]:
					FirstFillSheet[_RowLetter+str(_counter)] = batchHeaders
					FirstFillSheet.set_style(_RowLetter+str(_counter), styles.Style(font=Font(size=20, bold=True, )))
					_RowLetter = chr(ord(_RowLetter)+1)
				FirstFillSheet.row_dimensions[_counter].height = 40
				_counter+=1

				_RowLetter = "A"
				for batchInfoItems in unPickledData[4].keys():
					if not batchInfoItems == "INIT":
						for batch2ndHeaders in unPickledData[4][batchInfoItems]:
							FirstFillSheet[_RowLetter+str(_counter)] = unPickledData[4][batchInfoItems][batch2ndHeaders]
							_RowLetter = chr(ord(_RowLetter)+1)
						_counter+=1
				_counter+=1

				_RowLetter = "A"
				for palletHeaders in unPickledData[5]["INIT"]:
					FirstFillSheet[_RowLetter+str(_counter)] = palletHeaders
					FirstFillSheet.set_style(_RowLetter+str(_counter), styles.Style(font=Font(size=20, bold=True, )))
					_RowLetter = chr(ord(_RowLetter)+1)
				FirstFillSheet.row_dimensions[_counter].height = 40
				_counter+=1

				_RowLetter = "A"
				for palletInfoItems in unPickledData[5].keys():
					if not palletInfoItems == "INIT":
						for batch2ndHeaders in unPickledData[5][palletInfoItems]:
							FirstFillSheet[_RowLetter+str(_counter)] = unPickledData[5][palletInfoItems][batch2ndHeaders]
							_RowLetter = chr(ord(_RowLetter)+1)
						_counter+=1
				_counter+=1

				_RowLetter = "A"
				for QCHeaders in unPickledData[6]["INIT"]:
					FirstFillSheet[_RowLetter+str(_counter)] = QCHeaders
					FirstFillSheet.set_style(_RowLetter+str(_counter), styles.Style(font=Font(size=20, bold=True, )))
					_RowLetter = chr(ord(_RowLetter)+1)
				FirstFillSheet.row_dimensions[_counter].height = 40
				_counter+=1

				_RowLetter = "A"
				for QCInfoItems in unPickledData[6].keys():
					if not QCInfoItems == "INIT":
						for batch2ndHeaders in unPickledData[6][QCInfoItems]:
							FirstFillSheet[_RowLetter+str(_counter)] = unPickledData[6][QCInfoItems][batch2ndHeaders]
							_RowLetter = chr(ord(_RowLetter)+1)
						_counter+=1
				_counter+=1



				wb.save(self.WO_LogFolder+w0+".xlsx")#<<<<<<<<<<<<<<<<<<<<-------------------------------------------- Save the file
				print "Saved new Log: ", self.WO_LogFolder+w0+".xlsx", " Run: ", 1
			else:
				pass

		except IndexError, e:
			print "index error??????\n", e
		#except KeyError,e:
		#	print "fucking key error\n", e



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