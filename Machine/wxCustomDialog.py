# gridEvents.py

import wx
import wx.grid as gridlib
import random, math
from StateMachine import *

class NumberInputBox(wx.Dialog):
	def __init__(self, outputHeader, Buttons=["1","2","3","4","5","6","7","8","9","0","DEL",], ButtonSize=(75,75), multiLine =False):

		self._ButtonSize = ButtonSize
		self._TxtPannelheight = 100
		self._Border = (5, 5)
		self._NumOfButtonRows = 3
		self._outputHeader = outputHeader

		#The Size of our Dialog Boc
		self._Size = (2*(self._NumOfButtonRows*self._ButtonSize[0]+((self._NumOfButtonRows+1)*self._Border[0])),
			(self._NumOfButtonRows+3)*self._ButtonSize[1]+((self._NumOfButtonRows+3)*self._Border[1]))

		#Creates Dialog FrameWork
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL,
			size=self._Size)

		self.SetBackgroundColour((0,0,255))

		pan = wx.Panel(self, size=self._Size)

		#Meh Decides what size font i should use
		inputFont = wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,)

		##########################HEADER LAYER###################################

		if multiLine:
			self.Display_Output = wx.TextCtrl(pan,
				size=(self._Size[0]-self._Border[0]*2, self._TxtPannelheight),
				pos=self._Border,
				style=wx.TE_MULTILINE | wx.TE_CENTER)
		else:
			self.Display_Output = wx.TextCtrl(pan,
				size=(self._Size[0]-self._Border[0]*2, self._TxtPannelheight),
				pos=self._Border,
				style= wx.TE_CENTER)

		self.Display_Output.SetFont(inputFont)
		self.Display_Output.SetValue("<"+self._outputHeader+">")

		##########################BUTTON LAYERS###################################
		count = 1
		startingLeft = (self._Size[0]/2)-(1.5*self._ButtonSize[0])-self._Border[0]
		curPos = (startingLeft, self._TxtPannelheight+(self._Border[1]*2))

		for Button in Buttons:
			button = wx.Button(pan,
				label=Button,
				size=self._ButtonSize,
				pos=curPos)

			button.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
			button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )

			if Button == "+/-":
				button.SetForegroundColour((0, 255, 0))

			if count%self._NumOfButtonRows == 0:
				curPos = (startingLeft, curPos[1]+self._ButtonSize[1]+self._Border[1])
				count = 1
			else:
				curPos = (curPos[0]+self._Border[0]+self._ButtonSize[0], curPos[1])
				count += 1

		##########################Tidy Up###################################
		if not count == 1:
			curPos = (self._Border[0], curPos[1]+self._ButtonSize[1]+self._Border[1])
		else:
			curPos = (self._Border[0], curPos[1])

		opt_ok = wx.Button(pan, wx.ID_OK,label="OK",
			size=((self._Size[0]/2)-(self._Border[0]*1.5),45),
			pos=curPos)

		opt_close = wx.Button(pan, wx.ID_CANCEL, label="Cancel",
			size=((self._Size[0]/2)-(self._Border[0]*1.5),45),
			pos=((self._Size[0]/2)+(0.5*self._Border[0]),curPos[1]))

		##########################BOTOM LAYERS###################################
		self.SetMaxSize(self._Size)
		self.SetMinSize(self._Size)
		self.SetSize(self._Size)

	def OnButtonPress(self, event):
		#print "Got: ", event.GetEventObject().GetLabel(), event.GetEventObject().GetLabel() == "DEL"

		if self.Display_Output.GetValue() == "<"+self._outputHeader+">":
			self.Display_Output.SetValue("")
		theButton = event.GetEventObject()
		if theButton.GetLabel() == "DEL":
			if not self.Display_Output.GetValue()[-2:] == ", ":
				self.Display_Output.SetValue(self.Display_Output.GetValue()[:-1])
			else:
				self.Display_Output.SetValue(self.Display_Output.GetValue()[:-2])

		elif theButton.GetLabel() == ", ":
			if not self.Display_Output.GetValue()[-2:] == ", ":
				self.Display_Output.AppendText(", ")

		elif theButton.GetLabel() == "+/-":
			if self.Display_Output.GetValue().startswith("-"):
				self.Display_Output.SetValue(self.Display_Output.GetValue()[1:])
				theButton.SetForegroundColour((0, 255, 0)) # set text color
			else:
				self.Display_Output.SetValue("-"+self.Display_Output.GetValue())
				theButton.SetForegroundColour((255, 0, 0)) # set text color
		else:
			#print "appending: ", event.GetEventObject().GetLabel()
			self.Display_Output.AppendText(event.GetEventObject().GetLabel())

	def OnClose(self, event):
		self.Close(True)

	def getDialog(self):
		return self.Display_Output.GetValue()


class EmployeeRemoveBox(wx.Dialog):
	def __init__(self, outputHeader, currentLogger, ButtonSize=(175,50)):

		self._Border = (5, 5)
		self._ButtonSize = ButtonSize

		_emps= currentLogger.stillLoggedOn()
		_colums = math.ceil(math.sqrt(len(_emps)))


		self._Size  = (_colums*(self._Border[0]+ButtonSize[0])+self._Border[0], _colums*(self._Border[1]+ButtonSize[1])+self._Border[1]+200)

		#Creates Dialog FrameWork
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL)

		self.SetBackgroundColour((0,0,255))

		##################Create header & attach to BoxSizer #####################

		my_box = wx.StaticBox(self, wx.ID_ANY, "Employee Removal")
		_vbox = wx.StaticBoxSizer(my_box, wx.VERTICAL)

		self.display = wx.StaticText(self, -1, "Select Emplyee(s) To Remove", style=wx.TE_CENTER)
		self.display.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD, underline=True))
		self.display.SetSize(self.display.GetBestSize())
		self.display.SetForegroundColour((255,0,0)) # set text color

		_vbox.Add(self.display, flag=wx.ALIGN_CENTER, border=4)



		##################Create Grid Sizer & attach to BoxSizer #################
		self._gs = wx.GridSizer(_colums, _colums, self._Border[0], self._Border[1])

		self._employeeButtons = []

		for employeeTitle in ["Line_Leader","Mechanic","Line_Worker"]:
			for empNum, empTitle in sorted(_emps, key=lambda tup: tup[0]):
				if employeeTitle == empTitle:
					button=wx.Button(self, label=empNum), 0, wx.EXPAND
					button[0].Bind(wx.EVT_BUTTON, self.OnButtonPress, )
					self._employeeButtons.append(button)

		self._gs.AddMany(self._employeeButtons)
		_vbox.Add(self._gs, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)

		##################Create Ok and Cancle & attach to BoxSizer #################

		_hbox = wx.BoxSizer(wx.HORIZONTAL)

		_hbox.Add(wx.Button(self, wx.ID_OK,label="OK",
			size=((self._Size[0]/2)-(self._Border[0]*1.5),45)), flag=wx.ALIGN_LEFT, border=10)

		_hbox.Add(wx.Button(self, wx.ID_CANCEL, label="Cancel",
			size=((self._Size[0]/2)-(self._Border[0]*1.5),45)), flag=wx.ALIGN_RIGHT, border=10)

		_vbox.Add(_hbox, flag=wx.ALIGN_CENTER, border=10)

		self.SetSizer(_vbox)

		self.SetMaxSize(self._Size)
		self.SetMinSize(self._Size)
		self.SetSize(self._Size)

	def OnButtonPress(self, event):
		theButton = event.GetEventObject()

		#SetForegroundColour((255,0,0))
		#print theButton.GetBackgroundColour()
		if theButton.GetBackgroundColour() == (0,0,0,255):
			theButton.SetBackgroundColour((0,255,0,255))
		else:
			theButton.SetBackgroundColour((0,0,0,255))

	def OnClose(self, event):
		self.Close(True)

	def getSelection(self):

		_returns=[]
		for button in self._employeeButtons:
			if button[0].GetBackgroundColour() == (0, 255, 0, 255):
				_returns.append(button[0].GetLabel())

		return _returns


class BringLineDownBox(wx.Dialog):
	def __init__(self, outputHeader, reasons=["Maitenance","Inventory","Quality_Control","Break"], ButtonSize=(175,50)):

		self._Border = (5, 5)
		self._ButtonSize = ButtonSize

		#Creates Dialog FrameWork
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL)

		self.SetBackgroundColour((0,0,255))

		##################Create header & attach to BoxSizer #####################
		my_box = wx.StaticBox(self, wx.ID_ANY, "Bring line Down")
		_vbox = wx.StaticBoxSizer(my_box, wx.VERTICAL)

		self.display = wx.StaticText(self, -1, "Choose a Reason", style=wx.TE_CENTER)
		self.display.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD, underline=True))
		self.display.SetSize(self.display.GetBestSize())
		self.display.SetForegroundColour((255,0,0)) # set text color

		_vbox.Add(self.display, flag=wx.ALIGN_CENTER, border=4)

		##################Create Grid Sizer & attach to BoxSizer #################
		self._gs = wx.GridSizer(2, 2, self._Border[0], self._Border[1])

		self._employeeButtons = []

		for opition in reasons:
			button=wx.Button(self, label=opition), 0, wx.EXPAND
			button[0].Bind(wx.EVT_BUTTON, self.OnButtonPress, )
			self._employeeButtons.append(button)

		self._gs.AddMany(self._employeeButtons)
		_vbox.Add(self._gs, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)

		##################Create Ok and Cancle & attach to BoxSizer #################

		_hbox = wx.BoxSizer(wx.HORIZONTAL)

		_hbox.Add(wx.Button(self, wx.ID_OK, label="OK", size=ButtonSize))

		_hbox.Add(wx.Button(self, wx.ID_CANCEL, label="Cancel", size=ButtonSize))

		_vbox.Add(_hbox, flag=wx.ALIGN_CENTER, border=10)

		self.SetSizer(_vbox)

		#self.SetMaxSize(self._Size)
		#self.SetMinSize(self._Size)
		#self.SetSize(self._Size)

	def OnButtonPress(self, event):
		theButton = event.GetEventObject()

		for button in self._employeeButtons:
			button[0].SetBackgroundColour((0,0,0))

		#SetForegroundColour((255,0,0))
		if theButton.GetBackgroundColour() == (0,0,0,255):
			theButton.SetBackgroundColour((0,255,0,255))
		else:
			theButton.SetBackgroundColour((0,0,0,255))

	def getSelection(self):
		_returns=None
		for button in self._employeeButtons:
			if button[0].GetBackgroundColour() == (0, 255, 0):
				_returns=button[0].GetLabel()

		return _returns

class QWERTYBox(wx.Dialog):
	def __init__(self, outputHeader, ButtonSize=(175,50)):

		self._Border = (5, 5)
		self._ButtonSize = ButtonSize
		self._Size = (800,400)

		my_box = wx.StaticBox(self, wx.ID_ANY, outputHeader)
		_vbox = wx.StaticBoxSizer(my_box, wx.VERTICAL)

		#Creates Dialog FrameWork
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL)

		self.SetBackgroundColour((0,0,255))

		################################HEADER###################################
		self.Display_Output = wx.TextCtrl(self,
			style=wx.TE_MULTILINE | wx.TE_CENTER)


		self.Display_Output.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,))


		_vbox.Add(self.Display_Output, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=self._Border[0])

		self.SetSizer(_vbox)

		################################KEYBOARD#################################
		numbers=["1","2","3","4","5","6","7","8","9","0"]
		top = ["q","w","e","r","t","y","u","i","o","p"]
		mid = ["a","s","d","f","g","h","j","k","l", "DEL"]
		bot = ["CAP","z","x","c","v","b","n","m",".","/"]

		self._gs = wx.GridSizer(4, 10, self._Border[0], self._Border[1])

		self._Buttons = []
		self._cap = None

		for opition in numbers+top+mid+bot:
			if not opition == "":
				button=wx.Button(self, label=opition)
				if opition == "CAP":
					self._cap = button
				button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )
				button.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,))
				self._Buttons.append((button, 0, wx.EXPAND))
			else:
				self._Buttons.append((wx.StaticText(self), wx.EXPAND))


		self._gs.AddMany(self._Buttons)
		_vbox.Add(self._gs, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)

		button=wx.Button(self, label=" ", size=(self._Size[0], 50))
		button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )
		_vbox.Add(button, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=self._Border[0])


		##################Create Ok and Cancle & attach to BoxSizer #################

		_hbox = wx.BoxSizer(wx.HORIZONTAL)

		_hbox.Add(wx.Button(self, wx.ID_OK, label="OK", size=ButtonSize))

		_hbox.Add(wx.Button(self, wx.ID_CANCEL, label="Cancel", size=ButtonSize))

		_vbox.Add(_hbox, flag=wx.ALIGN_CENTER, border=10)

		#self.SetMaxSize(self._Size)
		#self.SetMinSize(self._Size)
		self.SetSize(self._Size)

	def OnButtonPress(self, event):
		theButton = event.GetEventObject()
		if theButton.GetLabel() == "DEL":
			self.Display_Output.SetValue(self.Display_Output.GetValue()[:-1])
		elif theButton.GetLabel() == "CAP":
			if theButton.GetBackgroundColour() == (0,0,0):
				theButton.SetBackgroundColour((0,255,0))
			else:
				theButton.SetBackgroundColour((0,0,0))
		else:
			if self._cap.GetBackgroundColour() == (0,0,0):
				self.Display_Output.AppendText(event.GetEventObject().GetLabel())
			else:
				self.Display_Output.AppendText(str(event.GetEventObject().GetLabel()).upper())



	def getDialog(self):
		return self.Display_Output.GetValue()

class InfoOptionBox(wx.Dialog):
	def __init__(self, outputHeader, currentLogger, option=1, ButtonSize=(175,50)):

		#Creates Dialog FrameWork
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL)

		################################Basic#################################

		self._Border = (5, 5)

		self.SetBackgroundColour((0,0,255))

		self.CurrentActivityLogger = currentLogger

		self.workingDict = None
		self._cap = None

		self._Buttons = dict()
		self._keys = []
		self.theAddButton = None

		self.currentOption = option

		if self.currentOption == 1:
			self.workingDict = self.CurrentActivityLogger.PalletInfo.copy()
		elif self.currentOption == 2:
			self.workingDict = self.CurrentActivityLogger.BatchInfo.copy()
		else:
			self.workingDict = self.CurrentActivityLogger.QCInfo.copy()


		################################KEYBOARD#################################

		self._vbox = wx.BoxSizer(wx.VERTICAL)
		self._currentGridSizer = wx.GridSizer(1, 1, self._Border[0], self._Border[1])
		self._vbox.Add(self._currentGridSizer, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)

		self.DrawDic()

		##################Create Ok and Cancle & attach to BoxSizer #################

		_hbox = wx.BoxSizer(wx.HORIZONTAL)

		_hbox.Add(wx.Button(self, wx.ID_OK, label="OK", size=ButtonSize))

		_hbox.Add(wx.Button(self, wx.ID_CANCEL, label="Cancel", size=ButtonSize))

		self._vbox.Add(_hbox, flag=wx.ALIGN_CENTER, border=10)

		#self._vbox.Add(self._currentGridSizer, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER)
		self.SetSizer(self._vbox)

		self._vbox.Fit(self)
		#self.SetSizer(self._vbox)
		#self._currentGridSizer.Fit(self)



	def DrawDic(self):

		#Reset Holding Vars
		self._cap = None
		self._Buttons = dict()
		self._keys = []
		self.theAddButton = None

		#Do Some Renameing and Clear the Gridsizer
		self._currentGridSizer.Clear(True)

		#Gets the keys of passed dictionary
		_dicKeys = self.workingDict.keys()

		#figures out needed rows and columbs for current gridsizer
		self._currentGridSizer.SetRows(len(_dicKeys)+1)
		self._currentGridSizer.SetCols(len(self.workingDict[_dicKeys[0]])+1)

		#print "Rows: ", len(_dicKeys)+1, "Cols: ", len(self.workingDict[_dicKeys[0]])+1
		#print self.CurrentActivityLogger

		#Add Blanck top left corner
		self._currentGridSizer.Add(wx.StaticText(self), 0, wx.EXPAND)

		#Adds the top header row
		for header in self.workingDict[sorted(_dicKeys)[-1]]:
			head = wx.StaticText(self, label=header, style=wx.ALIGN_CENTRE)
			head.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, underline=True,))

			self._currentGridSizer.Add(head, 0, wx.EXPAND)

		#Fills out every other button
		for count1, key in  enumerate(sorted(self.workingDict.keys())[:-1]):

			#Sorting Functionality
			if not (count1+1) == key:
				tmp = self.workingDict[key]
				del(self.workingDict[key])
				self.workingDict[count1+1] = tmp
				key = count1+1

			#Create The Key(Red) Button
			button = wx.Button(self, label=str(key))

			#Formats the button to look pretty
			button.Bind(wx.EVT_BUTTON, self.OnKeyPress, )
			button.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,))
			button.SetBackgroundColour((255, 0, 0))

			#Add keys to key and add the button to a list for later
			self._keys.append(button)
			self._currentGridSizer.Add(button, 0, wx.EXPAND,)

			for count2, item in enumerate(self.workingDict[key]):

				if self.currentOption == 1:

					if not count2 == 3:

						#Create Data Button
						button = wx.Button(self, label=str(item))

						#Formats the button to look pretty
						button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )

					else:
						button = wx.StaticText(self, label=str(item))

					button.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,))

					#Add keys to key and add the button to a list for later
					if not key in self._Buttons.keys():
						self._Buttons[key]=[]

					self._Buttons[key].append(button)
					self._currentGridSizer.Add(button, 0, wx.EXPAND)

				else:

					#Create Data Button
					button = wx.Button(self, label=str(item))

					#Formats the button to look pretty
					button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )

					button.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,))

					#Add keys to key and add the button to a list for later
					if not key in self._Buttons.keys():
						self._Buttons[key]=[]

					self._Buttons[key].append(button)
					self._currentGridSizer.Add(button, 0, wx.EXPAND)

		#Creates the green add button
		self.theAddButton = wx.Button(self, label="+")

		#Button Formating
		self.theAddButton.Bind(wx.EVT_BUTTON, self.OnNewLine, )
		self.theAddButton.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, underline=False,))
		self.theAddButton.SetBackgroundColour((0,255,0))

		#Add Button to GridSizer
		self._currentGridSizer.Add(self.theAddButton, 0, wx.EXPAND)

		#Fits the GridSizer to itself
		self._vbox.Fit(self)


	def OnNewLine(self, event):

		#Default text of newly added button row
		_initButtonText = ["N/A"]

		#If theres no existing lines just create 1
		if len(self.workingDict.keys()) == 1:
			self.workingDict[1] = len(self.workingDict["INIT"])*_initButtonText

		#else we apend to the bottom
		else:
			#print len(self.workingDict["INIT"]), ["N/A"]
			self.workingDict[sorted(self.workingDict.keys())[-2]+1] = len(self.workingDict["INIT"])*_initButtonText

		#Draw the new dictionarry
		self.DrawDic()


	def OnKeyPress(self, event):

		#Find Wich Button was pressed
		for button in self._keys:
			if event.GetEventObject() is button:

				#Delete the corisponding column in the dictionary
				del(self.workingDict[int(button.GetLabel())])

		#Draw the new dictionarry
		self.DrawDic()


	def OnButtonPress(self, event):

		#Draw the new dictionarry

		#pulls the button from the passed event
		theButton = event.GetEventObject()

		#Search for the button that
		for key in self._Buttons.keys():
			for pos, button in enumerate(self._Buttons[key]):
				if button is theButton:

					if (self.currentOption == 2 and pos == 0) or (self.currentOption == 1) or (self.currentOption == 3):

						if self.currentOption == 2 or self.currentOption == 3:
							dlg = QWERTYBox("Input Batch Number")
						else:
							dlg = NumberInputBox("Input Value", Buttons=["1","2","3","4","5","6","7","8","9","0",".","DEL",])

						if dlg.ShowModal() == wx.ID_OK:
							value = dlg.getDialog()

							self.workingDict[key][pos] = value
							theButton.SetLabel(value)

						dlg.Destroy()

					elif self.currentOption == 2:
						#keys: ("Tare Weight(g)","######"), ("Volume(ml)","######"), ("    Specific Gravity","######"), ("Weight(g)","######"), ("Cosmetic","######")
						# self.CurrentActivityLogger.fillSheet[key]
						keys = self.CurrentActivityLogger.fillSheet.keys()

						if pos == 1:
							if "Weight(g)" in keys and not self.CurrentActivityLogger.fillSheet["Weight(g)"] == "######" and not self.CurrentActivityLogger.fillSheet["Weight(g)"] == "N/A" :
								print self.CurrentActivityLogger.fillSheet["Weight(g)"]
								self.workingDict[key][pos] = float(self.CurrentActivityLogger.fillSheet["Weight(g)"])
								theButton.SetLabel(str(self.CurrentActivityLogger.fillSheet["Weight(g)"]))

							elif ("Volume(ml)" in keys and "    Specific Gravity" in keys) and not self.CurrentActivityLogger.fillSheet["Volume(ml)"] == "######" and not self.CurrentActivityLogger.fillSheet["    Specific Gravity"] == "######" and not self.CurrentActivityLogger.fillSheet["Volume(ml)"] == "N/A" and not self.CurrentActivityLogger.fillSheet["    Specific Gravity"] == "N/A":
								tmpValue = float(self.CurrentActivityLogger.fillSheet["Volume(ml)"])*float(self.CurrentActivityLogger.fillSheet["    Specific Gravity"])
								self.workingDict[key][pos] = tmpValue
								theButton.SetLabel(str(tmpValue))

							else:
								self.workingDict[key][pos] = None
								theButton.SetLabel("Invalid FS Data")

							if "Cosmetic" in keys and not self.CurrentActivityLogger.fillSheet["Cosmetic"] == "######" and not self.workingDict[key][pos] == None:
								tmpValue = self.workingDict[key][pos] + float(self.CurrentActivityLogger.fillSheet["Cosmetic"])
								self.workingDict[key][pos] = tmpValue
								theButton.SetLabel(str(tmpValue))

						elif pos == 2:
							if "Tare Weight(g)" in keys and not self.CurrentActivityLogger.fillSheet["Tare Weight(g)"] == "######":

								tmpValue = None
								try:
									tmpValue = float(self.workingDict[key][1])+float(self.CurrentActivityLogger.fillSheet["Tare Weight(g)"])
								except Exception, e:
									print e , self.workingDict[key][1], self.CurrentActivityLogger.fillSheet["Tare Weight(g)"]
									self.workingDict[key][pos] = None
									theButton.SetLabel("Invalid FS Data")
								else:
									self.workingDict[key][pos] = tmpValue
									theButton.SetLabel(str(tmpValue ))

							else:
								self.workingDict[key][pos] = None
								theButton.SetLabel("Invalid FS Data")
						else:
							try:
								tmpValue = 1.02*float(self.workingDict[key][2])
							except Exception, e:
								print e, self.workingDict[key][2]
								self.workingDict[key][pos] = None
								theButton.SetLabel("Invalid FS Data")
							else:
								tmpValue = str(float(self.workingDict[key][2]))+"-"+str(tmpValue)
								self.workingDict[key][pos] = tmpValue
								theButton.SetLabel(tmpValue)

					if self.currentOption==1:
							try:
								self.workingDict[key][3] = float(self.workingDict[key][1])*float(self.workingDict[key][2])
								self._Buttons[key][3].SetLabel(str(float(self.workingDict[key][1])*float(self.workingDict[key][2])))
							except Exception, e:
								self.workingDict[key][3] = "N/A"
								self._Buttons[key][3].SetLabel("N/A")

					else:
						pass

					#Fits the GridSizer to itself
					self._vbox.Fit(self)



	def GetDictionary(self):
		return self.workingDict

class Test(wx.Frame):
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, parent=None, title="An Eventful Grid")

				#Create The ActivityLogger
		self.CurrentActivityLogger = ActivityLogger(rpi=False)

		'''FOR TESTING PURPOSES ONLY'''
		for counter in range(25+int(random.random()*10)):
			self.CurrentActivityLogger.addEmployee(str(100+int(random.random()*50)))
		self.CurrentActivityLogger.addEmployee(str(322))
		self.CurrentActivityLogger.addEmployee(str(3131))
		self.CurrentActivityLogger.addEmployee(str(1441))

		# "Weight(g)" or "Volume(ml)" and "    Specific Gravity"
		self.CurrentActivityLogger.fillSheet["Volume(ml)"] = 10
		self.CurrentActivityLogger.fillSheet["    Specific Gravity"] = 10
		self.CurrentActivityLogger.fillSheet["Cosmetic"] = 0.5
		self.CurrentActivityLogger.fillSheet["Tare Weight(g)"] = 2.2

		#OPtion 3 QC Info
		newDic = {"INIT": ["Batch#","Stability","Begins","Middle","Ends","Re-Sample","Initials"],
									1: ['111', '100', '5', '500', '5', '500', '5'],
									2: ['121', '200', '5', '1000', '5', '500', '5'],}


		##########################SETS NEW Dictionary#############################
		self.CurrentActivityLogger._setQC(newDic)

		#OPtion 2 == batchInfo
		newDic = {"INIT": ["Batch Code", "Fill Weight", "Total Weight", "Total Wt Range"],
									1: ['111', '100', '5', '500'],
									2: ['121', '200', '5', '1000'],}

		##########################SETS NEW Dictionary#############################
		self.CurrentActivityLogger._setBatch(newDic)

		#OPtion 1 == PalletInfo
		newDic = {'INIT': ['Pallet#', 'Cases', 'Pcs/Case', 'Count', 'Batch#'],
									1: ['111', '100', '5', '500', '1123234'],
									2: ['121', '200', '5', '1000', '1423234'],}

		##########################SETS NEW Dictionary#############################
		self.CurrentActivityLogger._setPallet(newDic)


		dlg = EmployeeRemoveBox("Input Work Order Number", self.CurrentActivityLogger)

		result = dlg.ShowModal()
		dlg.Destroy()

		if result == wx.ID_OK:
			print "----------RESULT-----------"

			thedict = dlg.GetDictionary()

			for key in sorted(thedict.keys()):
				print key, thedict[key]

		else:
			print result

if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = Test().Show()
	app.MainLoop()