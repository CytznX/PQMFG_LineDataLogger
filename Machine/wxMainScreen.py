"""!/usr/bin/python2.7----------------------------------------------------------
Class that holds the Componets for the main view screen of PQMFG data aquistion system

Written by: Max Seifert AKA cytznx
-------------------------------------------------------------------------------"""

#Gui Elements
import wx
import datetime
from wxPython.wx import *

from StateMachine import *
from wxCustomDialog import NumberInputBox
from wxCustomDialog import EmployeeRemoveBox
from wxCustomDialog import BringLineDownBox

class mainScreenInfoPanel(wx.Panel):
	def __init__(self, parent, frame, passedLogger, hideMouse, size):

		# initialize Pannel
		wx.Panel.__init__(self, parent, size=size)

		self.Size = size

		#The Logger
		self.CurrentActivityLogger = passedLogger

		#Used for drawing employees
		self.previousEmpDicionary = []
		self.EmployeesDrawn = dict()

		#Hides the currser
		if hideMouse:
			self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

		#set Background color
		self.SetBackgroundColour("black")

		self.LocalBorder = 5

		# I save this ... for setting size later but i dont think i need to use it...
		self.myParent = parent

		#The Machine Number
		self.MachineNumberHeader = wx.StaticText(self, -1, self.CurrentActivityLogger.getMachineID(),
			pos =(1*self.LocalBorder,self.LocalBorder))

		#Basic Formating
		self.MachineNumberHeader.SetFont(wx.Font(40, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.MachineNumberHeader.SetSize(self.MachineNumberHeader.GetBestSize())
		self.MachineNumberHeader.SetForegroundColour((0,255,0)) # set text color
		self.MachineNumberHeader.SetBackgroundColour((0,0,255)) # set text back color


		#Creates the "PQMFG Data Aquision System________________ " Header
		mainHeader = wx.StaticText(self, -1, "PQMFG Data Aquision System________________ ",
			pos =((2*self.LocalBorder) + 91, 3.5*self.LocalBorder))

		#Basic Formating
		mainHeader.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
		mainHeader.SetSize(mainHeader.GetBestSize())
		mainHeader.SetForegroundColour((128,255,255)) # set text color
		#mainHeader.SetBackgroundColour((0,0,255)) # set text back color

		_FirstComnOffset = 5*self.LocalBorder
		_SecondOffset = 366
		_ThirdOffset = 700-30

		self._CountDspDic, returnLoc = self.CreateDspColumn(
			startingKeys = [("Total Peaces","######"), ("Peaces Boxed","######"), ("Peaces Scraped","######")],
			startingLoc = (_FirstComnOffset, self.MachineNumberHeader.GetBestSize()[1]+2*self.LocalBorder))

		self._PPMDspDic, returnLoc = self.CreateDspColumn(
			startingKeys = [("Hourly(Peaces/Minute)","###.##"), ("Total(Peaces/Minute)","###.##")],
			startingLoc = (_FirstComnOffset, returnLoc[1]+2*self.LocalBorder))

		self._LineStatusDspDic, returnLoc = self.CreateDspColumn(
			startingKeys = [("Current WO","N/A"), ("WO Runtime","00:00:00"), ("Line Status","Inactice")],
			startingLoc = (_SecondOffset,self.MachineNumberHeader.GetBestSize()[1]+2*self.LocalBorder),
			SecondColColor=(255, 0, 0))
		self._MnDwnTimesDspDic, returnLoc = self.CreateDspColumn(
			startingKeys = [("Maintence","00:00:00"), ("Inventory","00:00:00"), ("Q/A and Q/C","00:00:00"),("Break","00:00:00")],
			startingLoc = (_ThirdOffset,self.MachineNumberHeader.GetBestSize()[1]+2*self.LocalBorder),
			SecondColColor=(255, 0, 0))

		self._subDwnTimesDspDic, returnLoc = self.CreateDspColumn(
			startingKeys = [("Total","00:00:00"), ("Change Over","00:00:00")],
			startingLoc = (_ThirdOffset-7,returnLoc[1]+(2*self.LocalBorder)),
			SecondColColor=(255, 0, 0))

		#Creates the "PQMFG Data Aquision System________________ " Header
		subHeader = wx.StaticText(self, -1, "______Current Employees____________________________ ",
			pos =((2*self.LocalBorder) , returnLoc[1]+2*self.LocalBorder))

		#Basic Formating
		subHeader.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
		subHeader.SetSize(subHeader.GetBestSize())
		subHeader.SetForegroundColour((0,128,255)) # set text color
		#mainHeader.SetBackgroundColour((0,0,255)) # set text back color

		self._HeaderBottom = returnLoc[1]+2*self.LocalBorder + subHeader.GetBestSize()[1]

	def CreateDspColumn(self, startingKeys, startingLoc, Size=12, Spacers=(10,5), FirstColColor=(255, 255, 255), SecondColColor=(0, 255, 0)):
		curHeaderPos = startingLoc
		curHeaderSpacer = []

		#Dictionary Retured for updating pannels latter
		curDspDct = dict()

		#Create Static Text For keepping peace count
		for header,_ in startingKeys:

			curDspDct[header] = None
			subHeader = wx.StaticText(self, -1, header+": ",
				pos =curHeaderPos)

			subHeader.SetFont(wx.Font(Size, wx.SWISS, wx.NORMAL, wx.BOLD))
			subHeader.SetSize(subHeader.GetBestSize())
			subHeader.SetForegroundColour(FirstColColor) # set text color

			curHeaderPos = (curHeaderPos[0],curHeaderPos[1]+subHeader.GetBestSize()[1]+Spacers[1])

			curHeaderSpacer.append(subHeader.GetBestSize()[0])


		curHeaderPos = (curHeaderPos[0]+max(curHeaderSpacer)+Spacers[0], startingLoc [1])
		curHeaderSpacer = []

		for key, spacer in startingKeys:

			curDspDct[key] = wx.StaticText(self, -1, spacer,
				pos =curHeaderPos)

			curDspDct[key].SetFont(wx.Font(Size, wx.SWISS, wx.NORMAL, wx.BOLD))
			curDspDct[key].SetSize(curDspDct[key].GetBestSize())
			curDspDct[key].SetForegroundColour(SecondColColor) # set text color
			curHeaderSpacer.append(curDspDct[key].GetBestSize()[0])

			curHeaderPos = (curHeaderPos[0], curHeaderPos[1]+curDspDct[key].GetBestSize()[1]+Spacers[1])

		return curDspDct , (curHeaderPos[0]+max(curHeaderSpacer), curHeaderPos[1])

	def RefreshData(self):

		#self.CurrentActivityLogger.getMachineID()

		################################Update CurrentState##############################################
		current_WO, currentState, currentReason = self.CurrentActivityLogger.getCurrentState()

		try:
			self._LineStatusDspDic["Current WO"].SetLabel(current_WO)
			self._LineStatusDspDic["WO Runtime"].SetLabel("%02d:%02d:%02d" % self.CurrentActivityLogger.getRunTime())
		except TypeError:
			self._LineStatusDspDic["Current WO"].SetLabel(str(current_WO))
			self._LineStatusDspDic["WO Runtime"].SetLabel("N/A")

		if not currentState:
			self._LineStatusDspDic["Line Status"].SetLabel("Line Is Down")

			self.MachineNumberHeader.SetForegroundColour((255,0,0))
			self._LineStatusDspDic["Current WO"].SetForegroundColour((255,0,0))
			self._LineStatusDspDic["WO Runtime"].SetForegroundColour((255,0,0))
			self._LineStatusDspDic["Line Status"].SetForegroundColour((255,0,0))
		else:
			self._LineStatusDspDic["Line Status"].SetLabel("Line Is Up")

			self.MachineNumberHeader.SetForegroundColour((0,255,0))
			self._LineStatusDspDic["Current WO"].SetForegroundColour((0,255,0))
			self._LineStatusDspDic["WO Runtime"].SetForegroundColour((0,255,0))
			self._LineStatusDspDic["Line Status"].SetForegroundColour((0,255,0))

		################################Update DownTimes#################################################
		totalDwnTimes = self.CurrentActivityLogger.getDwnTimesTotals()

		for header,totals in zip(["Maintence","Inventory","Q/A and Q/C", "Break"],totalDwnTimes[:-1]):
			self._MnDwnTimesDspDic[header].SetLabel("%02d:%02d:%02d" % self.CurrentActivityLogger.formatDiffDateTime(totals))

		self._subDwnTimesDspDic["Change Over"].SetLabel("%02d:%02d:%02d" % self.CurrentActivityLogger.formatDiffDateTime(totalDwnTimes[-1]))
		self._subDwnTimesDspDic["Total"].SetLabel("%02d:%02d:%02d" % self.CurrentActivityLogger.formatDiffDateTime(sum(totalDwnTimes[:-1])))

		if not currentState and not currentReason =="ChangeOver":
			self._subDwnTimesDspDic["Total"].SetForegroundColour((255,0,0))

			if currentReason == "Maitenance":
				self._MnDwnTimesDspDic["Maintence"].SetForegroundColour((255,0,0))
			elif currentReason == "Inventory":
				self._MnDwnTimesDspDic["Inventory"].SetForegroundColour((255,0,0))
			elif currentReason == "Quality_Control":
				self._MnDwnTimesDspDic["Q/A and Q/C"].SetForegroundColour((255,0,0))
			elif currentReason == "Break":
				 self._MnDwnTimesDspDic["Break"].SetForegroundColour((255,0,0))
			else:
				for key in self._MnDwnTimesDspDic.keys():
					self._MnDwnTimesDspDic[key].SetForegroundColour((255,0,0))

		elif not currentState and currentReason =="ChangeOver":
			for key in self._MnDwnTimesDspDic.keys():
				self._MnDwnTimesDspDic[key].SetForegroundColour((0,255,0))

			self._subDwnTimesDspDic["Change Over"].SetForegroundColour((255,0,0))
			self._subDwnTimesDspDic["Total"].SetForegroundColour((0,255,0))

		else:
			for key in self._MnDwnTimesDspDic.keys():
				self._MnDwnTimesDspDic[key].SetForegroundColour((0,255,0))

			self._subDwnTimesDspDic["Change Over"].SetForegroundColour((0,255,0))
			self._subDwnTimesDspDic["Total"].SetForegroundColour((0,255,0))



		########################Update the counts########################################################
		totalCount, failCount, boxCount = self.CurrentActivityLogger.getCounts()
		#print totalCount, failCount, boxCount

		try:
			self._CountDspDic["Total Peaces"].SetLabel(str(sum(totalCount)))
			self._CountDspDic["Peaces Boxed"].SetLabel(str(sum(boxCount)))
			self._CountDspDic["Peaces Scraped"].SetLabel(str(failCount))
		except Exception, e:
			self._CountDspDic["Total Peaces"].SetLabel(str(totalCount))
			self._CountDspDic["Peaces Boxed"].SetLabel(str(boxCount))
			self._CountDspDic["Peaces Scraped"].SetLabel(str(failCount))


		#print self.CurrentActivityLogger.getCurrentRunningPassAvg(hourly=True), self.CurrentActivityLogger.getCurrentRunningPassAvg(hourly=False)

		try:
			self._PPMDspDic["Hourly(Peaces/Minute)"].SetLabel("%.2f" % self.CurrentActivityLogger.getCurrentRunningPassAvg(hourly=True))
			self._PPMDspDic["Total(Peaces/Minute)"].SetLabel("%.2f"% self.CurrentActivityLogger.getCurrentRunningPassAvg(hourly=False))
		except TypeError:
			self._PPMDspDic["Hourly(Peaces/Minute)"].SetLabel(str(self.CurrentActivityLogger.getCurrentRunningPassAvg(hourly=True)))
			self._PPMDspDic["Total(Peaces/Minute)"].SetLabel(str(self.CurrentActivityLogger.getCurrentRunningPassAvg(hourly=False)))

		if not self.previousEmpDicionary == self.CurrentActivityLogger.stillLoggedOn():

			EmpFont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
			CurrentPos = (5, self._HeaderBottom+5)
			ColumbWidths = []
			self.previousEmpDicionary = self.CurrentActivityLogger.stillLoggedOn()

			for key in self.EmployeesDrawn.keys():
				first = self.EmployeesDrawn[key][0]
				second = self.EmployeesDrawn[key][1]
				del self.EmployeesDrawn[key]
				first.Destroy()
				second.Destroy()

			self.EmployeesDrawn = dict()
			for Position in ["Line_Leader", "Mechanic","Line_Worker"]:

				if Position =="Line_Leader":
					posColor = (0,255,0)
				elif Position =="Mechanic":
					posColor = (128,0,64)
				elif Position =="Line_Worker":
					posColor = (0,0,255)

				for Employee_ID, Employee_Title in sorted(self.CurrentActivityLogger.stillLoggedOn(), key=lambda tup: tup[0]):
					if Position == Employee_Title:

						#Pull name from employee dictionary
						Employee_ID = self.CurrentActivityLogger.getName(Employee_ID)

						if Employee_ID == "Wayne Drown":
							empTitle = wx.StaticText(self, -1, "Princess"+":", pos=CurrentPos)
						elif Employee_ID == "Steven Mock":
							empTitle = wx.StaticText(self, -1, "Batman"+":", pos=CurrentPos)
						else:
							empTitle = wx.StaticText(self, -1, Employee_Title+":", pos=CurrentPos)
						empTitle.SetFont(EmpFont)
						nameSize = empTitle.GetBestSize()

						if CurrentPos[1]+5+nameSize[1] > self.Size[1] and ColumbWidths is not []:

							empTitle.Destroy()

							CurrentPos = (CurrentPos[0]+20+max(ColumbWidths), self._HeaderBottom+5)
							ColumbWidths = []

							if Employee_ID == "Wayne Drown":
								empTitle = wx.StaticText(self, -1, "Princess"+":", pos=CurrentPos)
							elif Employee_ID == "Steven Mock":
								empTitle = wx.StaticText(self, -1, "Batman"+":", pos=CurrentPos)
							else:
								empTitle = wx.StaticText(self, -1, Employee_Title+":", pos=CurrentPos)
							empTitle.SetFont(EmpFont)

						nameSize = empTitle.GetBestSize()
						empTitle.SetSize(nameSize)

						if Employee_ID == "Wayne Drown":
							empTitle.SetForegroundColour((255,0,255)) # set text color
						elif Employee_ID == "Steven Mock":
							empTitle.SetForegroundColour((255,255,0)) # set text color
						else:
							empTitle.SetForegroundColour(posColor) # set text color

						empNameColor = (255,255,255)

						empName = wx.StaticText(self, -1, Employee_ID, pos =(CurrentPos[0]+5+nameSize[0],CurrentPos[1]))

						empName.SetFont(EmpFont)
						empName.SetSize(empName.GetBestSize())
						empName.SetForegroundColour(empNameColor) # set text color

						ColumbWidths.append(5+nameSize[0]+empName.GetBestSize()[0])

						self.EmployeesDrawn[Employee_ID] = (empTitle, empName)

						CurrentPos = (CurrentPos[0], CurrentPos[1]+5+nameSize[1])
				CurrentPos = (CurrentPos[0], CurrentPos[1]+5)

class mainScreenButtonPanel(wx.Panel):

		def __init__(self, parent, frame, passedLogger, hideMouse, size,):

			#The Logger
			self.CurrentActivityLogger = passedLogger

			#Tagging Parent
			self.parent = parent
			self.curFrame = frame
			self.gap = 5

			#some universal variables
			self.button_width = (size[0]-(3*self.gap))/2
			self.button_height = ((int(((2.0/3.0)*(size[1]))-(8*self.gap)))/7)
			self.dialog_width = (size[0])-(3*self.gap)
			self.dialog_height = ((1.0/3.0)*(size[1])) - (3*self.gap)

			self.gap = self.gap

			# Create the Button/Message Panel
			wx.Panel.__init__(self, parent, size=size)
			#Hides the currser
			if hideMouse:
				self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			# set Background color
			self.SetBackgroundColour("black")

			# 1 Create Button Loading in New Work Order
			LoadNewWOButton = wx.Button(self, label="Load New WO",
				pos=(self.gap, self.gap), size=(self.button_width, self.button_height))

			LoadNewWOButton.Bind(wx.EVT_BUTTON, self.LoadNewWOButtonEvent, )

			# 2 Create Button for Deleting in New Work Order
			DeletWOButton = wx.Button(self, label="Delete Current WO",
				pos=(self.gap, 2*self.gap+1*self.button_height),
				size=(self.button_width, self.button_height))

			DeletWOButton.Bind(wx.EVT_BUTTON, self.DeletWOButtonEvent, )

			# 3 Create Button for adding Employee
			AddEmployeeButton = wx.Button(self, label="Add Employee",
				pos=(self.gap, 3*self.gap+2*self.button_height),
				size=(self.button_width, self.button_height))

			AddEmployeeButton.Bind(wx.EVT_BUTTON, self.AddEmployeeButtonEvent, )

			# 4 Create Button for Bring Line out of down time
			LineUpButton = wx.Button(self, label="Bring Line Up",
				pos=(self.gap, 4*self.gap+3*self.button_height),
				size=(self.button_width, self.button_height))

			LineUpButton.Bind(wx.EVT_BUTTON, self.LineUpButtonEvent, )

			#
			########################SECOND COLUM##################################
			#

			# 5 Create Button for Completing the current WO
			CompleteCurrentWOButton = wx.Button(self, label="Complete Current WO",
				pos=(2*self.gap + self.button_width, self.gap),
				size=(self.button_width, self.button_height))

			CompleteCurrentWOButton.Bind(wx.EVT_BUTTON, self.CompleteCurrentWOButtonEvent, )

			# 6 Create Button for adding Adjusting the Current WO Count
			AdjustCountButton = wx.Button(self, label="Adjust Current Count",
				pos=(2*self.gap + self.button_width, 2*self.gap+1*self.button_height),
				size=(self.button_width, self.button_height))

			AdjustCountButton.Bind(wx.EVT_BUTTON, self.AdjustCountButtonEvent, )

			# 7 Create Button for REmoving the current Employee
			removeEmployeeButton = wx.Button(self, label="Remove Employee",
				pos=(2*self.gap + self.button_width, 3*self.gap+2*self.button_height),
				size=(self.button_width, self.button_height))

			removeEmployeeButton.Bind(wx.EVT_BUTTON, self.removeEmployeeButtonEvent, )

			# 8 Create Button for Bringing Line Down
			LineDownButton = wx.Button(self, label="Bring Line Down",
				pos=(2*self.gap + self.button_width, 4*self.gap+3*self.button_height),
				size=(self.button_width, self.button_height))

			LineDownButton.Bind(wx.EVT_BUTTON, self.LineDownButtonEvent, )


			#
			########################Bottom Row##################################
			#

			# Create Button for switching view to fill sheet
			FillSheetButton = wx.Button(self, label="Fill Sheet",
				pos=(self.gap, 5*self.gap+4*self.button_height),
				size=((self.button_width*2)+self.gap, self.button_height))

			FillSheetButton.Bind(wx.EVT_BUTTON, self.FillSheetButtonEvent, )

			# 12 Create Button for seting Email Updates
			SetEmailButton = wx.Button(self, label="Set Email Updates",
				pos=(self.gap, 6*self.gap+5*self.button_height),
				size=((self.button_width*2)+self.gap, self.button_height))

			SetEmailButton.Bind(wx.EVT_BUTTON, self.SetEmailButtonEvent, )

			# 13Create Button for seting the printer
			SetPrinterButton = wx.Button(self, label="Set Printer",
				pos=(self.gap, (7*self.gap)+(6*self.button_height)),
				size=((self.button_width*2)+self.gap, self.button_height))

			SetPrinterButton.Bind(wx.EVT_BUTTON, self.SetPrinterButtonEvent, )

			#
			########################Readout Pannel ##################################
			#

			self._messagePannel = wx.TextCtrl( self, -1,
				pos=(self.gap, (8*self.gap)+(7*self.button_height)),
				size = (self.dialog_width, self.dialog_height),
				style = wx.TE_MULTILINE | wx.TE_READONLY)

			if hideMouse:
				LoadNewWOButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				DeletWOButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				AddEmployeeButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				LineUpButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				CompleteCurrentWOButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				AdjustCountButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				removeEmployeeButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				LineDownButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				FillSheetButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				SetEmailButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
				SetPrinterButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))


		def LoadNewWOButtonEvent(self, event=None):

			if self.CurrentActivityLogger.getCurrentState()[0] is None:
				dlg = NumberInputBox("Input WO#")
				result = dlg.ShowModal()

				if result == wx.ID_OK:
					self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S>')+" Loaded New WO: "+dlg.getDialog()+"\n")
					self.CurrentActivityLogger.changeCurrentWO(dlg.getDialog())
					self.CurrentActivityLogger.changeState("000", "ChangeOver")
					dlg.Destroy()

			else:
				dlg = wx.MessageDialog(self, "Cannot load new Work Order with out Completeing/Deleting current WO", "Warning WO Still Running", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()

		def DeletWOButtonEvent(self, event=None):

			current_WO, currentState, currentReason = self.CurrentActivityLogger.getCurrentState()

			#If theres no current workorer running
			if current_WO is not None:

				#Ask iif you want to quit
				dlg = wx.MessageDialog(self,
					"Do you really want to Delete Current Work Order: "+current_WO,
					"Confirm Exit", wx.YES_NO |wx.ICON_QUESTION)
				result = dlg.ShowModal()
				dlg.Destroy()

				#If selection was yes ... bail out
				if result == wx.ID_YES:
					self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S>')+" Deleted WO:"+current_WO+"\n")
					self.CurrentActivityLogger.changeCurrentWO(None, False)

			else:
				dlg = wx.MessageDialog(self, "No Work Order Currently Running", "Error", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()

		def AddEmployeeButtonEvent(self, event=None):

			dlg = NumberInputBox("Input Employee ID#", Buttons=["1","2","3","4","5","6","7","8","9","0",", ","DEL",], multiLine=True)
			result = dlg.ShowModal()
			dlg.Destroy()

			if result == wx.ID_OK:
				for returns in dlg.getDialog().split(", "):
					if not returns == "":
						self.CurrentActivityLogger.addEmployee(returns)
						self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S> ')+"Added Employee: "+self.CurrentActivityLogger.getName(returns)+"\n")

		def LineUpButtonEvent(self, event=None):
			if not self.CurrentActivityLogger.getCurrentState()[0] == None:
				dlg = NumberInputBox("Input Badge#")
				result = dlg.ShowModal()

				if result == wx.ID_OK:
					self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S> ')+self.CurrentActivityLogger.getName(dlg.getDialog())+" Brought Line Up from "+self.CurrentActivityLogger.getCurrentState()[2]+"\n")
					self.CurrentActivityLogger.changeState(dlg.getDialog())
					dlg.Destroy()

		def CompleteCurrentWOButtonEvent(self, event=None):

			status = self.CurrentActivityLogger.getCurrentState()
			if status[0] is not None:
				dlg = wx.MessageDialog(self,
					"Do you really want to Complete Work Order: "+status[0]+"?",
					"Confirm Complete WO", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
				result = dlg.ShowModal()
				dlg.Destroy()
				if result == wx.ID_OK:
					self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S>')+" Completed Work Order: "+status[0]+"\n")
					self.CurrentActivityLogger.finishCurrentWO()

		def AdjustCountButtonEvent(self, event=None):
			if self.CurrentActivityLogger.getCurrentState()[0] is not None:
				dlg = NumberInputBox("Input Badge#", Buttons=["1","2","3","4","5","6","7","8","9","0","DEL",])

				if dlg.ShowModal() == wx.ID_OK:
					ID = dlg.getDialog()
					dlg.Destroy()

					dlg = NumberInputBox("Input Amount", Buttons=["1","2","3","4","5","6","7","8","9","0","+/-","DEL",])

					if dlg.ShowModal() == wx.ID_OK:
						amount = dlg.getDialog()
						dlg.Destroy()

						self.CurrentActivityLogger.inc_CurTotalCount(event=None, amount=int(amount), force=True, ID=ID)
						self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S> ')+self.CurrentActivityLogger.getName(ID)+" adjusted count by: "+amount+" peaces\n")

			else:
				dlg = wx.MessageDialog(self, "Cannot Adjust Count Without First Loading in a new WO", "Warning no WO running", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()

		def removeEmployeeButtonEvent(self, event=None):

			dlg = EmployeeRemoveBox("Input Employee Number to be Removed", self.CurrentActivityLogger)
			result = dlg.ShowModal()
			dlg.Destroy()

			if result == wx.ID_OK:
				for employee in dlg.getSelection():
					self.CurrentActivityLogger.removeEmployee(employee)
					self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S> ')+"Removed Employee: "+employee+"\n")
			else:
				print result

		def LineDownButtonEvent(self, event=None):

			if self.CurrentActivityLogger.getCurrentState()[0] is not None and self.CurrentActivityLogger.getCurrentState()[1] is not False:
				dlg = NumberInputBox("Input Badge#", Buttons=["1","2","3","4","5","6","7","8","9","0","DEL",])

				if dlg.ShowModal() == wx.ID_OK:
					ID = dlg.getDialog()
					dlg.Destroy()

					dlg = BringLineDownBox("Input Work Order Number")

					result = dlg.ShowModal()
					output = dlg.getSelection()
					dlg.Destroy()

					if result == wx.ID_OK:
						self.CurrentActivityLogger.changeState(ID, output)
						self.WriteToTextPannel(datetime.datetime.now().strftime('<%H:%M:%S> ')+self.CurrentActivityLogger.getName(ID)+" Brought Line Down from "+output+"\n")

			else:
				dlg = wx.MessageDialog(self, "Cannot Adjust Machine State Without First Loading in a new WO or bringing the machine up first", "Warning no WO running", wx.OK)
				dlg.ShowModal()
				dlg.Destroy()

#####################################################################333



		def FillSheetButtonEvent(self, event=None):
			if self.CurrentActivityLogger.getCurrentState()[0] is not None:
				self.curFrame.TogglFillSheet(event)
			else:
				dlg = wx.MessageDialog(self,
					"You must load a Work Order before accessing Fillsheet",
					"Error", wx.OK)
				result = dlg.ShowModal()
				dlg.Destroy()


		def SetPrinterButtonEvent(self, event=None):
			pass

		def SetEmailButtonEvent(self, event=None):
			pass

		def UndoFilter(self):
			pass


		def WriteToTextPannel(self, MessageString):
			if(not(MessageString == None)):
				self._messagePannel.AppendText(MessageString)
