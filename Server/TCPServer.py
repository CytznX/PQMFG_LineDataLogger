#!/usr/bin/env python

import sys

import socket, os
import datetime, time
import pickle

import re
import MySQLdb
import _mysql

from threading import Thread
from openpyxl import styles
from openpyxl import *
from openpyxl.styles import Alignment
from openpyxl.styles import Font
class ThreadedTCPNetworkAgent(Thread):

	'''Default constructor... Much Love'''
	def __init__(self, portNum, Folder='WorkOrderExcelLogs', BuffSize=1024):

		#Initialize myself as thread... =P
		Thread.__init__(self)

		#setup some class variables
		self.running = True
		self.DefaultClientPort = 5005
		self._BuffSize = BuffSize
		self.Addr = ('', portNum)

		self.CurrentLines = dict()

		#self.IsMachineAlive = Thread(target=self.whoIsAlive, args=())
		#self.IsMachineAlive.start()

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
		can_continue = False
		now = datetime.datetime.now()

		#PULL IN NEW
		while True:
			data = clientsock.recv(self._BuffSize)

			#Heres we check to see if we have any data
			if not data:
				if safety is not "":
					can_continue = True
				break


			elif data.startswith("#KILL") or (safety+data).startswith("#KILL"):
				self.stop()
				break

			safety += data

		if can_continue:
			print "Processing Connection", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			try:

				unPickledData = pickle.loads(safety)

				w0 = unPickledData[0]["WO"]
				if not os.path.isfile(self.WO_LogFolder+w0 +".xlsx"):

					#Create a new
					wb = Workbook()
					headerSheet = wb.active

					headerSheet.title = "Work Order Sumary"
					headerSheet['A1'] = "WO#: "
					headerSheet['B1'] = w0

					headerSheet['A1'].style = styles.Style(font=Font(size=20, bold=True), alignment=Alignment(horizontal="right"))
					headerSheet['B1'].style = styles.Style(font=Font(size=20, bold=True), alignment=Alignment(horizontal="left"))

					#Creates Headers For Data Columbs
					headerSheet['A3'] = "Run#"
					headerSheet['A3'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['B3'] = "Start Time"
					headerSheet['B3'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['C3'] = "EndTime Time"
					headerSheet['C3'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['D3'] = "Total Count"
					headerSheet['D3'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['E3'] = "Total Box"
					headerSheet['E3'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['F3'] = "Total Fail"
					headerSheet['F3'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['A4'] = "------------"
					headerSheet['A4'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['B4'] = "------------"
					headerSheet['B4'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['C4'] = "------------"
					headerSheet['C4'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['D4'] = "------------"
					headerSheet['D4'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['E4'] = "------------"
					headerSheet['E4'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					headerSheet['F4'] = "------------"
					headerSheet['F4'].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="center"))

					#1"Run#" 2"Start Time" 3"EndTime Time" 4"Total Count" 5"Total Box" 6"Total Tossed"

					headerSheet['A5'] = "1"
					headerSheet['A5'].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['B5'] = unPickledData[0]["WO StartTime"].strftime('(%D) @ %H:%M:%S')
					headerSheet['B5'].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['C5'] = unPickledData[0]["Time Log Created"].strftime('(%D) @ %H:%M:%S')
					headerSheet['C5'].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['D5'] = sum(unPickledData[0]["Total Count"])
					headerSheet['D5'].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['E5'] = sum(unPickledData[0]["Box Count"])
					headerSheet['E5'].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['F5'] = unPickledData[0]["Fail Count"]
					headerSheet['F5'].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet.column_dimensions["A"].width = 15.0
					headerSheet.column_dimensions["B"].width = 30.0
					headerSheet.column_dimensions["C"].width = 30.0
					headerSheet.column_dimensions["D"].width = 15.0
					headerSheet.column_dimensions["E"].width = 15.0
					headerSheet.column_dimensions["F"].width = 15.0

					headerSheet.row_dimensions[1].height = 40

					FirstSheet = wb.create_sheet()
					FirstSheet.title = 'Run#1'

					FirstFillSheet = wb.create_sheet()
					FirstFillSheet.title = 'FillSheet#1'

				else:

					wb = load_workbook(self.WO_LogFolder+w0+'.xlsx')

					headerSheet = wb.get_sheet_by_name("Work Order Sumary")

					curNumRuns = (len(wb.get_sheet_names())-1)/2

					headerSheet['A'+str(5+curNumRuns)] = str(curNumRuns+1)
					headerSheet['A'+str(5+curNumRuns)].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['B'+str(5+curNumRuns)] = unPickledData[0]["WO StartTime"].strftime('(%D) @ %H:%M:%S')
					headerSheet['B'+str(5+curNumRuns)].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['C'+str(5+curNumRuns)] = unPickledData[0]["Time Log Created"].strftime('(%D) @ %H:%M:%S')
					headerSheet['C'+str(5+curNumRuns)].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['D'+str(5+curNumRuns)] = sum(unPickledData[0]["Total Count"])
					headerSheet['D'+str(5+curNumRuns)].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['E'+str(5+curNumRuns)] = sum(unPickledData[0]["Box Count"])
					headerSheet['E'+str(5+curNumRuns)].style = styles.Style(alignment=Alignment(horizontal="center"))

					headerSheet['F'+str(5+curNumRuns)] = unPickledData[0]["Fail Count"]
					headerSheet['F'+str(5+curNumRuns)].style = styles.Style(alignment=Alignment(horizontal="center"))

					FirstSheet = wb.create_sheet()
					FirstSheet.title = 'Run#'+str(curNumRuns+1)

					FirstFillSheet = wb.create_sheet()
					FirstFillSheet.title = 'FillSheet#'+str(curNumRuns+1)

				_preOrderedKeys = ["Machine ID", "WO", "Bulk Wo", "WO StartTime", "Time Log Created", "Total Count", "Box Count", "Fail Count", "Peaces Per Box", "Fill Start", "Fill End"]
				_TimedKeys = ["WO StartTime", "Time Log Created", "Fill Start", "Fill End"]

				_LastColumb = 1
				for key in _preOrderedKeys:
					if not key in _TimedKeys:

						FirstSheet['A'+str(_LastColumb)] = key
						FirstSheet['A'+str(_LastColumb)].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="left"))

						try:
							FirstSheet['B'+str(_LastColumb)] = unPickledData[0][key]
							FirstSheet['B'+str(_LastColumb)].style = styles.Style(alignment=Alignment(horizontal="center"))

						except KeyError,e:
							print "Woopc... Passed dictionary didnt contain Key: ",key

						except ValueError, e:

							FirstSheet['B'+str(_LastColumb)] = sum(unPickledData[0][key])
							FirstSheet['B'+str(_LastColumb)].style = styles.Style(alignment=Alignment(horizontal="center"))
							_LastColumb += 1

							FirstSheet['A'+str(_LastColumb)] = "^^^Hrly"
							FirstSheet['A'+str(_LastColumb)].style = styles.Style(alignment=Alignment(horizontal="left"))

							FirstSheet['B'+str(_LastColumb)] = str(unPickledData[0][key])
							FirstSheet['B'+str(_LastColumb)].style = styles.Style(alignment=Alignment(horizontal="center"))

					else:
						try:
							FirstSheet['A'+str(_LastColumb)] = key
							FirstSheet['A'+str(_LastColumb)].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="left"))

							if not unPickledData[0][key] == None:
								FirstSheet['B'+str(_LastColumb)] = unPickledData[0][key].strftime('(%D) @ %H:%M:%S')
							else:
								FirstSheet['B'+str(_LastColumb)] = "N/A"
							FirstSheet['B'+str(_LastColumb)].style = styles.Style(alignment=Alignment(horizontal="center"))
						except:
							print "uh oh something went wrong...", key

					_LastColumb += 1
				_LastColumb += 1

				#get keys from working employee dictionary
				empKeys = unPickledData[1].keys()
				_Postitions = ["Line_Leader", "Line_Worker", "Mechanic"]

				#heres the methodolagy for itterating over employee dictionary
				for pos in _Postitions:

					FirstSheet['A'+str(_LastColumb)] = '----'+pos+'(s)----'
					FirstSheet['A'+str(_LastColumb)].style = styles.Style(font=Font(bold=True), alignment=Alignment(horizontal="left"))
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
				FirstSheet['A'+str(_LastColumb)].style = styles.Style(font=Font(bold=True))
				_LastColumb += 1

				for adjCounts in unPickledData[0]["Line Var Adjustments"]:
					FirstSheet['A'+str(_LastColumb)] = '('+str(adjCounts[0])+', '+str(adjCounts[1])+', '+str(adjCounts[2])+', '+adjCounts[3].strftime('%H:%M:%S')+')'
					_LastColumb += 1

				_LastColumb += 1
				FirstSheet['A'+str(_LastColumb)] = '---Down Time----'
				FirstSheet['A'+str(_LastColumb)].style = styles.Style(font=Font(bold=True))
				_LastColumb += 1

				FirstSheet['A'+str(_LastColumb)] = 'Maintanance> '+str(unPickledData[2]["FormattedMain"][0])+':'+str(unPickledData[2]["FormattedMain"][1])+':'+str(unPickledData[2]["FormattedMain"][2])
				_LastColumb+=1

				for start,end in unPickledData[0]["Maintanance Down Times"]:
					maintainMsg = ""
					if not end == None:
						maintainMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						maintainMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

					FirstSheet['A'+str(_LastColumb)] = maintainMsg
					_LastColumb+=1
				_LastColumb+=1

				FirstSheet['A'+str(_LastColumb)] = 'Inventory> '+str(unPickledData[2]["FormattedInv"][0])+':'+str(unPickledData[2]["FormattedInv"][1])+':'+str(unPickledData[2]["FormattedInv"][2])
				_LastColumb+=1

				for start,end in unPickledData[0]["Inventory Down Time"]:
					InventoryMsg = ""
					if not end == None:
						InventoryMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						InventoryMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

					FirstSheet['A'+str(_LastColumb)] = InventoryMsg
					_LastColumb+=1
				_LastColumb+=1

				FirstSheet['A'+str(_LastColumb)] = 'Quality_Control> '+str(unPickledData[2]["FormattedQuality"][0])+':'+str(unPickledData[2]["FormattedQuality"][1])+':'+str(unPickledData[2]["FormattedQuality"][2])
				_LastColumb+=1
				for start,end in unPickledData[0]["Quality Control Down Time"]:
					QualityControlMsg = ""
					if not end == None:
						QualityControlMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						QualityControlMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '

					FirstSheet['A'+str(_LastColumb)] = QualityControlMsg
					_LastColumb+=1
				_LastColumb+=1

				FirstSheet['A'+str(_LastColumb)] = 'Break> '+str(unPickledData[2]["FormattedBreak"][0])+':'+str(unPickledData[2]["FormattedBreak"][1])+':'+str(unPickledData[2]["FormattedBreak"][2])
				_LastColumb+=1


				for start,end in unPickledData[0]["Break Down Time"]:
					breakMsg = ""
					if not end == None:
						breakMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						breakMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '
					FirstSheet['A'+str(_LastColumb)] = breakMsg
					_LastColumb+=1
				_LastColumb+=1

				FirstSheet['A'+str(_LastColumb)] = 'ChangeOver> '+str(unPickledData[2]["FormattedChngOvr"][0])+':'+str(unPickledData[2]["FormattedChngOvr"][1])+':'+str(unPickledData[2]["FormattedChngOvr"][2])
				_LastColumb+=1

				for start,end in unPickledData[0]["ChangeOver Time"]:
					breakMsg = ""
					if not end == None:
						breakMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+' '+str(end[1])+')) '
					else:
						breakMsg += '(('+start[0].strftime('%H:%M:%S')+' '+str(start[1])+'),('+now.strftime('%H:%M:%S')+' N/A)) '
					FirstSheet['A'+str(_LastColumb)] = breakMsg
					_LastColumb+=1
				_LastColumb+=1


				FirstSheet['A'+str(_LastColumb)] = 'Total> '+str(unPickledData[2]["FormattedTotal"][0])+':'+str(unPickledData[2]["FormattedTotal"][1])+':'+str(unPickledData[2]["FormattedTotal"][2])
				FirstSheet['A'+str(_LastColumb)].style = styles.Style(font=Font(bold=True))
				_LastColumb+=2

				FirstSheet.column_dimensions["A"].width = 30.0
				FirstSheet.column_dimensions["B"].width = 30.0

				FirstFillSheet['A1'] = "WO#: "
				FirstFillSheet['B1'] = w0
				FirstFillSheet['C1'] = "Fill SHEET "
				FirstFillSheet.row_dimensions[1].height = 40

				FirstFillSheet['A1'].style =  styles.Style(font=Font(size=20, bold=True, ), alignment=Alignment(horizontal="right"))
				FirstFillSheet['B1'].style = styles.Style(font=Font(size=20, bold=True, ), alignment=Alignment(horizontal="center"))
				FirstFillSheet['C1'].style = styles.Style(font=Font(size=20, bold=True, ), alignment=Alignment(horizontal="left"))

				_counter = 2
				for fillSheetItems in unPickledData[3].keys():
					FirstFillSheet['A'+str(_counter)] = fillSheetItems
					FirstFillSheet['B'+str(_counter)] = unPickledData[3][fillSheetItems]
					FirstFillSheet['A'+str(_counter)].style = styles.Style(font=Font(bold=True, ))
					_counter += 1
				_counter += 1

				_RowLetter = "A"
				for batchHeaders in unPickledData[4]["INIT"]:
					FirstFillSheet[_RowLetter+str(_counter)] = batchHeaders
					FirstFillSheet[_RowLetter+str(_counter)].style = styles.Style(font=Font(size=15, bold=True, ))
					_RowLetter = chr(ord(_RowLetter)+1)
				FirstFillSheet.row_dimensions[_counter].height = 40
				_counter += 1


				for batchInfoItems in unPickledData[4].keys():
					_RowLetter = "A"
					if not batchInfoItems == "INIT":
						for batch2ndHeaders in unPickledData[4][batchInfoItems]:
							FirstFillSheet[_RowLetter+str(_counter)] = batch2ndHeaders
							FirstFillSheet[_RowLetter+str(_counter)].style = styles.Style(alignment=Alignment(horizontal="center"))
							_RowLetter = chr(ord(_RowLetter)+1)
						_counter += 1
				_counter += 1

				_RowLetter = "A"
				for palletHeaders in unPickledData[5]["INIT"]:
					FirstFillSheet[_RowLetter+str(_counter)] = palletHeaders
					FirstFillSheet[_RowLetter+str(_counter)].style = styles.Style(font=Font(size=15, bold=True, ))
					_RowLetter = chr(ord(_RowLetter)+1)
				FirstFillSheet.row_dimensions[_counter].height = 40
				_counter+=1

				for palletInfoItems in unPickledData[5].keys():
					_RowLetter = "A"
					if not palletInfoItems == "INIT":
						for batch2ndHeaders in unPickledData[5][palletInfoItems]:
							FirstFillSheet[_RowLetter+str(_counter)] = batch2ndHeaders
							FirstFillSheet[_RowLetter+str(_counter)].style = styles.Style(alignment=Alignment(horizontal="center"))
							_RowLetter = chr(ord(_RowLetter)+1)
						_counter+=1
				_counter+=1

				_RowLetter = "A"
				for QCHeaders in unPickledData[6]["INIT"]:
					FirstFillSheet[_RowLetter+str(_counter)] = QCHeaders
					FirstFillSheet[_RowLetter+str(_counter)].style = styles.Style(font=Font(size=15, bold=True, ))
					_RowLetter = chr(ord(_RowLetter)+1)
				FirstFillSheet.row_dimensions[_counter].height = 40
				_counter+=1


				for QCInfoItems in unPickledData[6].keys():
					_RowLetter = "A"
					if not QCInfoItems == "INIT":
						for batch2ndHeaders in unPickledData[6][QCInfoItems]:
							FirstFillSheet[_RowLetter+str(_counter)] = batch2ndHeaders
							FirstFillSheet[_RowLetter+str(_counter)].style = styles.Style(alignment=Alignment(horizontal="center"))
							_RowLetter = chr(ord(_RowLetter)+1)
						_counter+=1
				_counter+=1

				FirstFillSheet.column_dimensions["A"].width = 30.0
				FirstFillSheet.column_dimensions["B"].width = 30.0
				FirstFillSheet.column_dimensions["C"].width = 30.0
				FirstFillSheet.column_dimensions["D"].width = 30.0
				FirstFillSheet.column_dimensions["E"].width = 30.0
				FirstFillSheet.column_dimensions["F"].width = 30.0

				FirstFillSheet.row_dimensions[1].height = 40

				wb.save(self.WO_LogFolder+w0+".xlsx")#<<<<<<<<<<<<<<<<<<<<-------------------------------------------- Save the file
				print "Saved new Log: ", self.WO_LogFolder+w0+".xlsx", " Run: ", (len(wb.get_sheet_names())-1)/2

				self.writeToSQL(str((len(wb.get_sheet_names())-1)/2), unPickledData)

				print"------------------------END-OF_LOG("+self.WO_LogFolder+w0+".xlsx)"+"------------------------\n"

			except IndexError, e:
				print "index error??????\n", e
		#except KeyError,e:
		#	print "fucking key error\n", e


	def writeToSQL(self, RunNum, MachineLog, databaseConectionVars=("192.168.20.31","cyrus","cyrus2sql","pqmfg_daq")):
		sql = []
		NOW = datetime.datetime.now()

		#-------------------------------------------------------------------------------
		#--------------------------WORKORDER_RUNS---------------------------------------
		#-------------------------------------------------------------------------------

		woRunSQLVars = ["WORKORDER_NUM", "RUN_NUM","MACHINE_NUM", "RUN_START", "RUN_END", "FILL_START", "FILL_END",
									"TOTAL_COUNT", "TOTAL_BOXED", "TOTAL_SCRAPPED", "TARE_WEIGHT", "VOLUME", "SPECIFIC_GRAVITY",
									"WEIGHT", "Cosmetic",	"ITEM_NUMBER", "DESIRED_QTY", "FORMULA_REF_NUM","PACKING_CODE", "PACK_OFF",
									"PUMP_NUM", "SIMPLEX_NUM"]

		#---------------------------------ZIP---------------------------------------

		machineQuery = ["WORKORDER_NUM", "MACHINE_NUM", "RUN_START",
										"RUN_END", "FILL_START", "FILL_END", "TOTAL_COUNT",
										"TOTAL_BOXED", "TOTAL_SCRAPPED"]

		machineDictKeys= ["WO","Machine ID", "WO StartTime", "Time Log Created",
											"Fill Start", "Fill End", "Total Count", "Box Count",
											"Fail Count"]

		#---------------------------------ZIP2--------------------------------------

		fillSheetQuery = ["TARE_WEIGHT", "VOLUME", "SPECIFIC_GRAVITY", "WEIGHT",
											"Cosmetic",	"ITEM_NUMBER", "DESIRED_QTY", "FORMULA_REF_NUM",
											"PACKING_CODE", "PACK_OFF", "PUMP_NUM", "SIMPLEX_NUM"]

		fillSheetDictKeys = ["Tare Weight(g)", "Volume(ml)", "    Specific Gravity",
												"Weight(g)", "Cosmetic", "Item Number", "Desired Qty",
												"Formula Ref#", "Packing Code", "Pack Off", "Pump#",
												"Simplex#"]

		VarHeaders = ""
		EndingString = ""

		for MV_DicKey, MV_SQLKey in zip (machineDictKeys,machineQuery):

			if MV_DicKey in MachineLog[0].keys():
				VarHeaders += MV_SQLKey+", "
				if MachineLog[0][MV_DicKey] == None:
					EndingString += "'NULL', "
				else:
					if MV_SQLKey.endswith("_END") or MV_SQLKey.endswith("_START"):

						if MachineLog[0][MV_DicKey] is not None:
							EndingString += "'"+MachineLog[0][MV_DicKey].strftime('%Y-%m-%d %H:%M:%S')+ "', "

						else:
							EndingString += "'"+str(MachineLog[0][MV_DicKey])+"', "

					elif MV_SQLKey == "RUN_NUM":
						EndingString += "'"+str(RunNum)+"', "

					elif MV_SQLKey == "TOTAL_BOXED" or MV_SQLKey == "TOTAL_COUNT":
						EndingString += "'"+str(sum(MachineLog[0][MV_DicKey]))+"', "

					else:
						EndingString += "'"+str(MachineLog[0][MV_DicKey])+"', "

		for FS_DicKey, FS_SQLKey in zip(fillSheetDictKeys, fillSheetQuery):
			if FS_DicKey in MachineLog[3].keys():
				VarHeaders += FS_SQLKey+", "
				if MachineLog[3][FS_DicKey] == None:
					EndingString += "'NULL', "
				else:
					EndingString += "'"+str(MachineLog[3][FS_DicKey])+"', "


		sql.append("INSERT INTO WORKORDER_RUNS ("+VarHeaders[:-2]+") VALUES ("+EndingString[:-2]+");")

		#-------------------------------------------------------------------------------
		#--------------------------DOWNTIMES--------------------------------------------
		#-------------------------------------------------------------------------------

		#1) Maitenance, 2) Inventory, 3) Quality_Control 4) Break 5) ChangeOver
		# 'ChangeOver','Maitenance','Inventory','Quality_Control','Break'
		# WORKORDER_NUM, RUN_NUM, TYPE, START, END, EMP_BD, EMP_BU
		VarHeaders = "WORKORDER_NUM, MACHINE_NUM, RUN_NUM, TYPE, START, END, EMP_BD, EMP_BU"
		EndingString = ""

		ChangeDwnTime = ("ChangeOver", MachineLog[0]["ChangeOver Time"])
		MainDwnTime = ("Maitenance", MachineLog[0]["Maintanance Down Times"])
		InvDwnTime = ("Inventory", MachineLog[0]["Inventory Down Time"])
		QualDwnTime = ("Quality_Control", MachineLog[0]["Quality Control Down Time"])
		BreakDwnTime = ("Break", MachineLog[0]["Break Down Time"])

		for reason, DWN_Tmes in [ChangeDwnTime, MainDwnTime, InvDwnTime, QualDwnTime, BreakDwnTime]:

			for DWN_Tme in DWN_Tmes:

				if DWN_Tme[1] is not None:
					sql.append("INSERT INTO DOWNTIMES ("+VarHeaders+") VALUES ( '%s','%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[0]["WO"], MachineLog[0]["Machine ID"], str(RunNum), reason, DWN_Tme[0][0].strftime('%Y-%m-%d %H:%M:%S'), DWN_Tme[1][0].strftime('%Y-%m-%d %H:%M:%S'), DWN_Tme[0][1], DWN_Tme[1][1]))
				else:
					sql.append("INSERT INTO DOWNTIMES ("+VarHeaders+") VALUES ( '%s','%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[0]["WO"], MachineLog[0]["Machine ID"], str(RunNum), reason, DWN_Tme[0][0].strftime('%Y-%m-%d %H:%M:%S'), NOW.strftime('%Y-%m-%d %H:%M:%S'), DWN_Tme[0][1], "000"))

		#-------------------------------------------------------------------------------
		#--------------------------EMPLOYEE_BADGE_SWIPES--------------------------------
		#-------------------------------------------------------------------------------

		VarHeaders = "EMPLOYEE_BADGE_NUM, EMP_TYPE, MACHINE_NUM, WORKORDER_NUM, RUN_NUM, TIME_IN, TIME_OUT"

		for key in MachineLog[1].keys():
			for times in MachineLog[1][key][1]:

				starttime = times[0].strftime('%Y-%m-%d %H:%M:%S')
				endtime = times[1]

				if endtime is not None:
					endtime = endtime.strftime('%Y-%m-%d %H:%M:%S')
				else:
					endtime = NOW.strftime('%Y-%m-%d %H:%M:%S')

				sql.append("INSERT INTO EMPLOYEE_BADGE_SWIPES ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s','%s');" % (key, MachineLog[1][key][0], MachineLog[0]["Machine ID"], MachineLog[0]["WO"], str(RunNum), starttime, endtime))


		#-------------------------------------------------------------------------------
		#-----------------------------------PALLETS-------------------------------------
		#-------------------------------------------------------------------------------
		if len(MachineLog[6].keys()) > 1:
			VarHeaders = "PALLET_NUM, BATCH_NUM, WORKORDER_NUM, RUN_NUM, BOXES, PEACES_PER_BOX"

			for key in MachineLog[5].keys():
				if not type(key) is str:
					sql.append("INSERT INTO PALLETS ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s');" % (MachineLog[5][key][0], MachineLog[5][key][4], MachineLog[0]["WO"], str(RunNum), MachineLog[5][key][1], MachineLog[5][key][2]))

		#-------------------------------------------------------------------------------
		#-----------------------------------BATCHES-------------------------------------
		#-------------------------------------------------------------------------------
		if len(MachineLog[4].keys()) > 1:
			VarHeaders = "BATCH_NUM, WORKORDER_NUM, MACHINE_NUM, RUN_NUM, FILL_WEIGHT, TOTAL_WEIGHT, TOTAL_WEIGHT_RANGE"

			for key in MachineLog[4].keys():
				if not type(key) is str:
					sql.append("INSERT INTO BATCHES ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[4][key][0], MachineLog[0]["WO"], MachineLog[0]["Machine ID"], str(RunNum), MachineLog[4][key][1], MachineLog[4][key][2], MachineLog[4][key][3]))

		#-------------------------------------------------------------------------------
		#------------------------------------QC-----------------------------------------
		#-------------------------------------------------------------------------------
		if len(MachineLog[6].keys()) > 1:
			VarHeaders = "MACHINE_NUM, WORKORDER_NUM, RUN_NUM, BATCH_NUM, STABILITY, BEGINS, MIDDLE, ENDS, RESAMPLE, INITIALS"

			for key in MachineLog[6].keys():
				if not type(key) is str:
					sql.append("INSERT INTO QC ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[0]["Machine ID"], MachineLog[0]["WO"], str(RunNum), MachineLog[6][key][0], MachineLog[6][key][1], MachineLog[6][key][2], MachineLog[6][key][3], MachineLog[6][key][4], MachineLog[6][key][5], MachineLog[6][key][6]))

		#-------------------------------------------------------------------------------
		#----------------------------------FINALLY--------------------------------------
		#-------------------------------------------------------------------------------

		# Open database connection
		db = MySQLdb.connect(databaseConectionVars[0], databaseConectionVars[1], databaseConectionVars[2], databaseConectionVars[3])

		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		for SQL_Statment in sql:
			try:
				# Execute the SQL command
				print "SQL: ", SQL_Statment
				cursor.execute(SQL_Statment)
				# Commit your changes in the database
				db.commit()

			except _mysql.Error, e:
				db.rollback()
				print "SQL Error %d: %s" % (e.args[0], e.args[1])

			except:
				# Rollback in case there is any error
				db.rollback()

		# disconnect from server
		db.close()




	def writeFile(self, FileName, Content , write ="w"):
		myfile = open(FileName, write)
		for newLine in Content:
			myfile.write(newLine+'\n')
		myfile.close()

	def stop(self):
		#set runflag to False

		if self.testing: print "Setting RunFlag to False"
		self.running = False

		#if self.testing: print "Waiting for alive thread to join"
		#self.IsMachineAlive.join()

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
	a = ThreadedTCPNetworkAgent(5006, Folder="/media/windowsshare/Operations/WorkOrderExcelLogs")
	a.start()