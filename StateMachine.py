'''
This is Version 2.0 of the PQMFG state machine feature improved as well as simplified functionality

Created By: Maxwell Seifert

'''
rpi = False

#Import the needed moduals
import time, datetime, string, socket
import PQMFG_TCPClient 

if rpi:
	import RPi.GPIO as GPIO

#I added this variable so i could easily enable and disable the piface digital I/O stuff

class ActivityLogger:
	'''
	Default constructor... Much Love
	'''
	def __init__(self, logFolder = 'LogFolder/'):

		#creates class variabls for passed or called constructor Vars
		self.logfolder = logFolder
		self.createInitVars()

		#If this isnt being tested on my computer initialize piface

		#The TCP server that waits for commands and is allowed to pull data from logger
		self.CurrentTCPServer = PQMFG_TCPClient.ThreadedTCPNetworkAgent(self, self.port)
		self.CurrentTCPServer.start()

		#Current WO that is being run
		self.current_WO = None

		#Keeps Track Of current State
		self.currentState = None
		self.currentReason = None

		#When Was this WO started on the Line
		self.WO_StartTime = None

		#last hour increment/decrement time
		self.hourIncrement = None
		self.hourdecrement = None

		#Keeps Track Of Pass/Fail Count
		self.totalCount = None
		self.failCount = None
		self.boxCount = None
		self.peacesPerBox = None
		
		#Arraylist of what count adjustments took place and when
		self.adjustments = []

		#Keeps Track of total down time
		self.MaintananceDwnTime = []
		self.InventoryDwnTime = []
		self.QualityControlDwnTime = []

		#Keeps track of all logged in employees
		self.EmpWorkingDic = dict()
		self.EmployeeRef = self.createEmployeeDic()

		if rpi:
			#Initialize GPIO mode
			GPIO.setmode(GPIO.BCM)

			# GPIO 23 & 24 set up as inputs, pulled up to avoid false detection.
			# Both ports are wired to connect to GND on button press.
			# So we'll be setting up falling edge detection for both
			GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

			# when a falling edge is detected on port 24, regardless of whatever 
			# else is happening in the program, the function my_callback will be run
			GPIO.add_event_detect(24, GPIO.FALLING, callback=self.inc_CurTotalCount, bouncetime=300)

			# when a falling edge is detected on port 23, regardless of whatever 
			# else is happening in the program, the function my_callback2 will be run
			# 'bouncetime=300' includes the bounce control written into interrupts2a.py
			GPIO.add_event_detect(23, GPIO.FALLING, callback=self.inc_CurBoxCount, bouncetime=300)
	
	def release(self):
		if rpi:
			GPIO.cleanup()
		self.CurrentTCPServer.stop()
		self.CurrentTCPServer.join()

	def getCounts(self):
		return self.totalCount, self.failCount, self.boxCount, self.peacesPerBox

	def getMachineID(self):
		return self.MachineID

	def getStartTime(self):
		return self.WO_StartTime

	def createInitVars(self, DefaultFile = 'MachineInitVar.txt', ErrorLog = 'ErrorLog.txt'):

		ErrorLog = self.logfolder+ErrorLog

		#Initialized as default values
		self.MachineID = '1'
		self.port= 5005
		self.FserverIP = '127.0.0.1'
		self.FserverPort = 5005

		recievedlines = []

		try:

			f = open(DefaultFile, "r")#open
			recievedlines = f.readlines()#read
			f.close()#close... <3
			Readfile = True

				#if for some reason we cant open the file 
		except IOError, e:

			#writes to ErrorLog.txt
			logfile = open(ErrorLog, "a")

			logfile.write( "--WARNING--------------------------")
			logfile.write( "\n"+time.ctime())
			logfile.write( "\nError: "+str(e) )
			logfile.write( "\nDesc: Failed To retreive Initial Machine Var Data")
			logfile.write( "\n-----------------------------------\n")
			logfile.close()
			recievedlines =[]

		except IndexError, e:
			#writes to ErrorLog.txt
			logfile = open(ErrorLog, "a")

			logfile.write( "--WARNING--------------------------")
			logfile.write( "\n"+time.ctime())
			logfile.write( "\nError: "+str(e) )
			logfile.write( "\nDesc: "+DefaultFile+" is formated wrong")
			logfile.write( "\n-----------------------------------\n")
			logfile.close()
			recievedlines=[]

		#read all lines and look for what I want ... yuuuuuuupppp
		for line in recievedlines:
			if line.startswith('MachineNumber'):
				self.MachineID = line.split()[1]
			
			elif line.startswith('MachinPort'):
				try:
					self.port = int(line.split()[1])
				except ValueError:
					self.port = 5005
			
			elif line.startswith('ServerIP'):
				self.FserverIP = line.split()[1]

			elif line.startswith('ServerPort'):
				try:
					self.FserverPort = int(line.split()[1])
				except ValueError:
					self. FserverPort = 5005

	'''
	Opens up the employee.txt file and returns data as a python dictionary
	'''
	def createEmployeeDic(self, EmployeeFile = 'employee.txt'):

		returnedDictionary = dict()
		lines =[]
		try:
			f = open(EmployeeFile, "r")#open
			lines = f.readlines()#read
			f.close()#close... <3

		#if for some reason we cant open the file 
		except IOError, e:

			#writes to ErrorLog.txt
			logfile = open("/home/pi/PQMFG/ErrorLog.txt", "a")
			#Print out an ERROR MESSAGE to the terminal
			logfile.write( "--WARNING--------------------------")
			logfile.write( "\nTime: "+ str(datetime.date.today()) +" @ " 
									+ str(time.localtime()[3])+":"
									+ str(time.localtime()[4]))

			logfile.write( "\nError: "+str(e) )
			logfile.write( "\nDesc: Failed To retreive Employee Reference Data")
			logfile.write( "\n-----------------------------------\n")
			logfile.close()

		#itterate over the lines and break everything apart
		for line in lines:
			FormatedStrings = [x.strip() for x in line.split(',')]
			returnedDictionary[FormatedStrings[0]] = FormatedStrings[1],FormatedStrings[2]+" "+FormatedStrings[3]

		#return the newly created didctionary
		return returnedDictionary
	
	'''
	Add Employee to working dict
	'''
	def addEmployee(self, EmployName = '-1' , Id = 'Line_Worker'):

		#used as return to determine succsess of operation 
		result = False

		#If the employee is a line leader or mechanic grab the actual name
		if EmployName in self.EmployeeRef:
			Name = EmployName
			EmployName = self.EmployeeRef[Name][1]
			Id = self.EmployeeRef[Name][0]

		#Checks to see if worker has been logged in already, if he/she hasnt add them directly to dic
		if EmployName not in self.EmpWorkingDic:

			#Create new key value if none is found
			self.EmpWorkingDic[EmployName]=(Id,[(datetime.datetime.now(), None)])
			result = True 
		
		#if the worker has already been logged in ignore loggin request and return false
		elif self.EmpWorkingDic[EmployName][1][-1][1] == None:

			#If already logged in due nothing and retrun false
			result = False

		#if we get here the only other option is to add to current worker chain
		else:

			#else add new loggin to dict()
			self.EmpWorkingDic[EmployName][1].append((datetime.datetime.now(),None))
			result = True 

		return result
	
	'''
	Logs employee out of working dictionary 
	'''
	def removeEmployee(self, EmployName = '-1'):

		#used as return to determine succsess of operation 
		result = False

		#If the employee is a line leader or mechanic grab the actual name
		if EmployName in self.EmployeeRef:
			Name = EmployName
			EmployName = self.EmployeeRef[Name][1]
			Id = self.EmployeeRef[Name][0]

		#make sure that the employee exists in the dictionary and that he/she hasnt been logged out yet
		if (EmployName in self.EmpWorkingDic) and (self.EmpWorkingDic[EmployName][1][-1][1] == None):

			#log worker out
			inTime = self.EmpWorkingDic[EmployName][1][-1][0]
			self.EmpWorkingDic[EmployName][1][-1] = (inTime, datetime.datetime.now())
			result = True

		return result

	'''
	Logs employee out of working dictionary 
	'''
	def getName(self, ID):
		if ID in self.EmployeeRef:
			return self.EmployeeRef[ID][1]

		else:
			return ID

	def stillLoggedOn(self):

		#The current employees that are in dictionary file
		curentkeys = self.EmpWorkingDic.keys()

		#The ToBeReturned list that will contain all employees that 
		stillLoggedOn =[]

		#iterates over all employees and looks for the ones with no logout time
		for key in curentkeys:
			if self.EmpWorkingDic[key][1][-1][1] == None:
				stillLoggedOn.append((key,self.EmpWorkingDic[key][0]))

		#returns a list[]
		return stillLoggedOn

	'''
	Used to change the current workorder that is being run on the machine 
	'''
	def changeCurrentWO(self, WO_Name, SavePrevious = True):
		connected = False

		#If the machine has just started or in standby every thing is set to None so just initialize
		if not(self.current_WO == None) and SavePrevious:

			'''First Send all relivant OLD data via TCP to server'''
			connected = self.sendToServer(self.getFormatedLog())
			
		#Current WO that is being run
		self.current_WO = WO_Name

		#Keeps Track Of current State
		self.currentState = True
		self.currentReason = None

		#When Was this WO started on the Line

		self.WO_StartTime = datetime.datetime.now()
		self.hourIncrement = datetime.datetime.now()
		self.hourdecrement = datetime.datetime.now()

		#Keeps Track Of Pass/Fail Count
		self.totalCount = [0]
		self.failCount = [0]		
		self.boxCount = [0]
		self.peacesPerBox = None

		self.peacesPerBox = None

		#Keeps Track of count adjustments
		self.adjustments = []

		#Keeps Track of total down time
		self.MaintananceDwnTime = []
		self.InventoryDwnTime = []
		self.QualityControlDwnTime = []

		return connected

	def changePeacesPerBox(self, ppb):
		self.peacesPerBox = ppb

	def finishCurrentWO(self):
		#used for return statment
		finishSuccsess = False

		#checks first to see if machine has been initialized...
		if not self.currentState == None:

			'''Create TCP Client and make it send shit '''
			finishSuccsess = self.sendToServer(self.getFormatedLog())

			#Current WO that is being run
			self.current_WO = None

			#Keeps Track Of current State
			self.currentState = None
			self.currentReason = None

			#When Was this WO started on the Line
			self.WO_StartTime = None

			#last hour increment/decrement time
			self.hourIncrement = None
			self.hourdecrement = None

			#Keeps Track Of Pass/Fail Count
			self.totalCount = None
			self.failCount = None
			self.boxCount = None
			self.peacesPerBox = None

			#Keeps Track of count adjustments
			self.adjustments = []

			#Keeps Track of total down time
			self.MaintananceDwnTime = []
			self.InventoryDwnTime = []
			self.QualityControlDwnTime = []

		return finishSuccsess

	'''
	Used to bring machine up or down depending on currentState
	'''
	def changeState(self, ID, Reason = None):
		'''
		current possible reasons: 1)Maitenance, 2) Inventory, 3) Quality_Control
		-------------------------------------------------------------------------
		self.MaintananceDwnTime = []
		self.InventoryDwnTime = []
		self.QualityControlDwnTime = []
		'''

		#used for return statment
		wasChanged = False

		#checks first to see if machine has been initialized...
		if self.currentState == None:
			pass #if it has, do nothing

		#else we check to see what state its in and perform the corisponing operations
		#(if True)
		elif self.currentState and not Reason == None:

			#Change the State of the machine
			self.currentState = False

			#Change the return Var
			wasChanged = True

			if Reason == 'Maitenance':
				self.MaintananceDwnTime.append(((datetime.datetime.now(),ID), None))
				self.currentReason = Reason

			elif Reason == 'Inventory':
				self.InventoryDwnTime.append(((datetime.datetime.now(),ID), None))
				self.currentReason = Reason

			elif Reason == 'Quality_Control':
				self.QualityControlDwnTime.append(((datetime.datetime.now(),ID), None))
				self.currentReason = Reason

		#(if False)
		elif not self.currentState:
			#Change the State of the machine
			self.currentState = True


			#Change the return Var
			wasChanged = True

			if self.currentReason == 'Maitenance':
				#Close Maintanance Downtime
				placeholder = self.MaintananceDwnTime[-1][0]
				self.MaintananceDwnTime[-1] = (placeholder, (datetime.datetime.now(),ID))

			elif self.currentReason == 'Inventory':
				#Close Inventory Downtime
				placeholder = self.InventoryDwnTime[-1][0]
				self.InventoryDwnTime[-1] = (placeholder, (datetime.datetime.now(),ID))

			elif self.currentReason == 'Quality_Control':
				#Close QualityControlDwnTime Downtime
				placeholder = self.QualityControlDwnTime[-1][0]
				self.QualityControlDwnTime[-1] = (placeholder, (datetime.datetime.now(),ID))

			self.currentReason = None

		return wasChanged

	'''
	Used to tell what state the machine is currently in
	'''
	def getCurrentState(self):
		return (self.current_WO,self.currentState, self.currentReason)

	'''
	Used to Increment the current pass count on running work order
	'''
	def inc_CurTotalCount(self, event = None, amount = 1, force = False, ID = None):

		incrementSucssful = False
		if not self.current_WO == None and (not self.currentState == False or force):
			if amount==1 and ID == None:
				incrementSucssful = True

				#If more than a hour has passed start new tally and reset clock
				if (datetime.datetime.now()-self.hourIncrement).seconds >3600:
					self.hourIncrement = datetime.datetime.now()
					self.boxCount.append(0)
					self.failCount.append(0)
					self.totalCount.append(amount)

				#elses we increment current tally
				else:
					self.totalCount[-1] += amount


			elif (not amount == 1) or (not ID == None):
				self.adjustments.append((ID ,'Total', amount, datetime.datetime.now()))
				incrementSucssful = True

				#If more than a hour has passed start new tally and reset clock
				if (datetime.datetime.now()-self.hourIncrement).seconds >3600:
					self.hourIncrement = datetime.datetime.now()
					self.boxCount.append(0)
					self.failCount.append(0)
					self.totalCount.append(amount)

				#elses we increment current tally
				else:
					self.totalCount[-1] += amount

		self.refreshFailCount()
		return incrementSucssful
	'''
	Used to Increment the current fail count on running work order
	'''
	def refreshFailCount(self,  event = None, force = False):
		
		decrementSucssful = False

		if not self.current_WO == None and (not self.currentState == False or force):
			decrementSucssful = True

			#If more than a hour has passed start new tally and reset clock
			if(datetime.datetime.now()-self.hourdecrement).seconds >3600:
				self.hourdecrement = datetime.datetime.now()
				self.boxCount.append(0)
				self.failCount.append(0)
				self.totalCount.append(0)

			#elses we increment current tally
			else:
				if not (self.totalCount==None or self.boxCount ==None or self.peacesPerBox == None):
					self.failCount[-1] = self.totalCount[-1] - (self.boxCount[-1]*self.peacesPerBox)
				else:
					self.failCount[-1] = 0

		return decrementSucssful

	def inc_CurBoxCount(self,  event = None, amount =1, force = False, ID = None):
		
		decrementSucssful = False

		if not self.current_WO == None and (not self.currentState == False or force):

			if amount==1 and ID == None:
				decrementSucssful = True

				#If more than a hour has passed start new tally and reset clock
				if(datetime.datetime.now()-self.hourdecrement).seconds >3600:
					self.hourdecrement = datetime.datetime.now()
					self.boxCount.append(amount)
					self.failCount.append(0)
					self.totalCount.append(0)

				#elses we increment current tally
				else:
					self.boxCount[-1] += amount

			elif not amount == 1 and not ID == None:
				self.adjustments.append((ID ,'Box', amount, datetime.datetime.now()))
				decrementSucssful = True

				#If more than a hour has passed start new tally and reset clock
				if(datetime.datetime.now()-self.hourdecrement).seconds >3600:
					self.hourdecrement = datetime.datetime.now()
					self.boxCount.append(amount)
					self.failCount.append(0)
					self.totalCount.append(0)

				#elses we increment current tally
				else:
					self.boxCount[-1] += amount

		self.refreshFailCount()
		return decrementSucssful

	'''
	returns the runtime (in seconds) of current work order
	'''
	def getRunTime(self, Formatted = True):
		runTime = None

		if not self.current_WO == None:
			#self.WO_StartTime = datetime.datetime.now()
			if Formatted:
				runTime = self.formatDiffDateTime((datetime.datetime.now()-self.WO_StartTime).seconds)
			else:
				runTime = (datetime.datetime.now()-self.WO_StartTime).seconds

		return runTime

	#return the Average PPM of all parts 
	def getCurrentRunningPassAvg(self, hourly = False):

		curAvg = None

		if not self.current_WO == None:
			try:

				if hourly:
					if not (self.peacesPerBox == None or self.peacesPerBox == 0):
						peacesPacked = self.boxCount[-1]*self.peacesPerBox
					else:
						peacesPacked = self.totalCount[-1]

					curAvg = peacesPacked/((datetime.datetime.now()-self.hourIncrement).seconds/60.0)

					
				else:
					if not (self.peacesPerBox == None or self.peacesPerBox == 0):
						peacesPacked = sum(self.boxCount)*self.peacesPerBox
					else:
						peacesPacked = sum(self.totalCount)

					curAvg = peacesPacked/(self.getRunTime(False)/60.0)

			except ZeroDivisionError:
					curAvg = 0
		return curAvg

	def getDwnTimesTotals(self):
		'''
		current possible reasons: 1)Maitenance, 2)Inventory, 3)Quality_Control
		-------------------------------------------------------------------------
		self.MaintananceDwnTime = []
		self.InventoryDwnTime = []
		self.QualityControlDwnTime = []
		'''

		Totals_Maitenance  = 0
		Totals_Inventory  = 0
		Totals_Quality_Control = 0

		for dwnTimes in self.MaintananceDwnTime:
			start = dwnTimes[0][0]

			if dwnTimes[1] == None:
				end = datetime.datetime.now()
			else:
				end = dwnTimes[1][0]

			Totals_Maitenance += (end-start).seconds

		for dwnTimes in self.InventoryDwnTime:
			start = dwnTimes[0][0]

			if dwnTimes[1] == None:
				end = datetime.datetime.now()
			else:
				end = dwnTimes[1][0]

			Totals_Inventory += (end-start).seconds

		for dwnTimes in self.QualityControlDwnTime:
			start = dwnTimes[0][0]
			if dwnTimes[1] == None:
				end = datetime.datetime.now()
			else:
				end = dwnTimes[1][0]

			Totals_Quality_Control += (end-start).seconds

		return (Totals_Maitenance, Totals_Inventory, Totals_Quality_Control)

	def sendToServer(self, data):
		succsesss = False
		try: 
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.FserverIP, self.FserverPort))

			for message in data:
				s.send(message)
				s.send('////')

			s.close()
			succsesss = True
		except socket.error:
			succsesss = False
			print "<<<<<<<<<<<<<<<Could not connect to server>>>>>>>>>>>>>>."
			for message in data:
				print message
			print '<<<<<<<<<<<<<<<END>>>>>>>>>>>>>>>>>>>>'
		return succsesss

	def getFormatedLog(self, stillRunning = False):

		#Initializes the log array as None (will be used in return later)
		log = []

		#Checks to see that there is actually a work order being run, before we create the log
		if not self.current_WO == None:

			#Assighnment of first attribute spots
			log = [self.current_WO, self.MachineID, self.WO_StartTime.strftime('(%D) @ %H:%M:%S')]

			now = datetime.datetime.now()

			#if machine is running Declare, otherwise assume W/O is finished
			if stillRunning:
				log += ['Running '+now.strftime('(%D) @ %H:%M:%S')]
			else:
				log += ['Finished ' +now.strftime('(%D) @ %H:%M:%S')]

			#add it to the current return log
			log +=[str(sum(self.totalCount)), str(sum(self.failCount)), str(sum(self.boxCount))]

			if not self.peacesPerBox == None:
				log +=[str(self.peacesPerBox)]
			else:
				log +=['']
			#get keys from working employee dictionary
			empKeys = self.EmpWorkingDic.keys()
			
			# temporrary storage arrays that help store all employees 
			lineworkers = ['----Line Worker(s)----']
			lineleaders = ['----Line Leader(s)----']
			lineMechanics = ['----Mechanic(s)----']

			#heres the methodolagy for itterating over employee dictionary 
			for key in empKeys:
				if(self.EmpWorkingDic[key][0]=="Line_Leader"):
					EmployOutputString = key+": "
					for x,y in self.EmpWorkingDic[key][1]:
						if y == None:
							y =  now

						if y > self.WO_StartTime:
							EmployOutputString += ' ('+x.strftime('%H:%M:%S')+','+y.strftime('%H:%M:%S') +') '

					lineleaders.append(EmployOutputString)

				elif(self.EmpWorkingDic[key][0]=="Line_Worker"):
					EmployOutputString = key+": "
					for x,y in self.EmpWorkingDic[key][1]:
						if y == None:
							y =  now

						if y > self.WO_StartTime:
							EmployOutputString += ' ('+x.strftime('%H:%M:%S')+','+y.strftime('%H:%M:%S') +') '

					lineworkers.append(EmployOutputString)

				elif(self.EmpWorkingDic[key][0]=="Mechanic"):
					EmployOutputString = key+": "
					for x,y in self.EmpWorkingDic[key][1]:
						if y == None:
							y =  now

						if y > self.WO_StartTime:
							EmployOutputString += ' ('+x.strftime('%H:%M:%S')+','+y.strftime('%H:%M:%S') +') '

					lineMechanics.append(EmployOutputString)

			#add the newly created lis together and append them to the current log file
			log+= lineleaders+lineworkers+lineMechanics

			dwntime = self.getDwnTimesTotals()

			#(Totals_Maitenance, Totals_Inventory, Totals_Quality_Control)

			FormattedTotal = self.formatDiffDateTime(sum(dwntime))
			FormattedMain = self.formatDiffDateTime(dwntime[0])
			FormattedInv = self.formatDiffDateTime(dwntime[1])
			FormattedQuality = self.formatDiffDateTime(dwntime[2])

			'''
			self.MaintananceDwnTime = []
			self.InventoryDwnTime = []
			self.QualityControlDwnTime = []
			'''

			adjustMessage=''
			for adjCounts in self.adjustments:
				adjustMessage+= '('+str(adjCounts[0])+', '+str(adjCounts[1])+', '+str(adjCounts[2])+', '+adjCounts[3].strftime('%H:%M:%S')+')' 
				
			log+=['---Adjustments----',adjustMessage,'']


			maintainMsg = ''
			for start,end in self.MaintananceDwnTime:
				if not end == None:
					maintainMsg += '(('+start[0].strftime('%H:%M:%S')+','+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+','+str(end[1])+')) '
				else: 
					maintainMsg += '(('+start[0].strftime('%H:%M:%S')+','+str(start[1])+'),('+now.strftime('%H:%M:%S')+',N/A)) '

			InventoryMsg = ''
			for start,end in self.InventoryDwnTime:
				if not end == None:
					InventoryMsg += '(('+start[0].strftime('%H:%M:%S')+','+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+','+str(end[1])+')) '
				else: 
					InventoryMsg += '(('+start[0].strftime('%H:%M:%S')+','+str(start[1])+'),('+now.strftime('%H:%M:%S')+',N/A)) '

			QualityControlMsg = ''
			for start,end in self.QualityControlDwnTime:
				if not end == None:
					QualityControlMsg += '(('+start[0].strftime('%H:%M:%S')+','+str(start[1])+'),('+end[0].strftime('%H:%M:%S')+','+str(end[1])+')) '
				else: 
					QualityControlMsg += '(('+start[0].strftime('%H:%M:%S')+','+str(start[1])+'),('+now.strftime('%H:%M:%S')+',N/A)) '

			log+=['---Down Time----',  
				'Maintanance> '+str(FormattedMain[0])+':'+str(FormattedMain[1])+':'+str(FormattedMain[2]),
				maintainMsg,
				'Inventory> '+str(FormattedInv[0])+':'+str(FormattedInv[1])+':'+str(FormattedInv[2]),
				InventoryMsg,
				'Quality_Control> '+str(FormattedQuality[0])+':'+str(FormattedQuality[1])+':'+str(FormattedQuality[2]),
				QualityControlMsg,
				'Total> '+str(FormattedTotal[0])+':'+str(FormattedTotal[1])+':'+str(FormattedTotal[2])]

		return log

	def formatDiffDateTime(self, TimeDiff):
		hours = TimeDiff/3600
		minutes =(TimeDiff-(hours*3600))/60
		sec = (TimeDiff-(hours*3600)-(minutes*60))
		return hours, minutes, sec
