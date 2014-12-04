"""!/usr/bin/python2.7----------------------------------------------------------
Class that holds the Componets for the Fill view screen of PQMFG data aquistion system

Written by: Max Seifert AKA cytznx
-------------------------------------------------------------------------------"""

#Gui Elements
import wx
import datetime
from wxPython.wx import *

from StateMachine import *
from wxCustomDialog import NumberInputBox

class fillScreenInfoPanel(wx.Panel):
	def __init__(self, parent, passedLogger, hideMouse, size):

		#Tagging Parent
		self.parent = parent

		#The Logger
		self.CurrentActivityLogger = passedLogger

		# initialize Pannel
		wx.Panel.__init__(self, parent, size=size)

		#Hides the currser
		if hideMouse:
			self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

		#set Background color
		self.SetBackgroundColour("black")

		self.LocalBorder = 5

		#Creates the "PQMFG Data Aquision System________________ " Header
		mainHeader = wx.StaticText(self, -1, "_______PQMFG Line Fill Sheet__________",
			pos =((2*self.LocalBorder), 4*self.LocalBorder))

		#Basic Formating
		mainHeader.SetFont(wx.Font(48, wx.SWISS, wx.NORMAL, wx.BOLD))
		mainHeader.SetSize(mainHeader.GetBestSize())
		mainHeader.SetForegroundColour((255,0,255)) # set text color
		#mainHeader.SetBackgroundColour((0,0,255)) # set text back color

		self._FillSheetHeaderVariables, returnLoc = self.CreateDspColumn(
			startingKeys = [("Work Order","######"), ("Run Start","00:00:00"), ("Run End","00:00:00"), ("Fill Start","00:00:00"), ("Fill End","00:00:00")],
			startingLoc = (12*self.LocalBorder, mainHeader.GetBestSize()[1]+(10*self.LocalBorder)),
			Size=24,
			SecondColColor=(255, 0, 0))

		for key in self._FillSheetHeaderVariables.keys():
			self._FillSheetHeaderVariables[key].Bind(wx.EVT_BUTTON, self.OnButtonPress, )

		self._FillSheetWeightsInfo, returnLoc = self.CreateDspColumn(
			startingKeys = [("Tare Weight(g)","######"), ("Volume(ml)","######"), ("    Specific Gravity","######"), ("Weight(g)","######"), ("Cosmetic","######")],
			startingLoc = (12*self.LocalBorder, size[1]-300-(10*self.LocalBorder)),
			Button = True,
			Size=24,
			SecondColColor=(255, 0, 0))

		for key in self._FillSheetWeightsInfo.keys():
			self._FillSheetWeightsInfo[key].Bind(wx.EVT_BUTTON, self.OnButtonPress, )

		colPos = 130+returnLoc[0]

		self._FillSheetProductInfo, returnLoc = self.CreateDspColumn(
			startingKeys = [("Product Name","######"), ("Formula Ref#","######"), ("Packing Code","######")],
			startingLoc = (colPos, mainHeader.GetBestSize()[1]+(10*self.LocalBorder)),
			Button = True,
			Size=24,
			SecondColColor=(255, 0, 0))

		for key in self._FillSheetProductInfo.keys():
			self._FillSheetProductInfo[key].Bind(wx.EVT_BUTTON, self.OnButtonPress, )

		# 0 Create Button for Pack Off selection
		self.packOff = wx.Button(self, label="Pack Off",
			pos=(returnLoc[0]-550, returnLoc[1]), size=(533, 50))

		self.packOff.SetForegroundColour((0,0,0)) # set text color
		self.packOff.SetBackgroundColour((255,0,0)) # set text color

		self._FillSheetEquipment, returnLoc = self.CreateDspColumn(
			startingKeys = [("Pump#","######"), ("Simplex#","######")],
			startingLoc = (colPos, returnLoc[1] + 60),
			Button = True,
			Size=24,
			SecondColColor=(255, 0, 0))

		for key in self._FillSheetEquipment.keys():
			self._FillSheetEquipment[key].Bind(wx.EVT_BUTTON, self.OnButtonPress, )

		# 1 Create Button for returning view to mainSheet
		BackButton = wx.Button(self, label="Back",
			pos=(size[0]-200-(10*self.LocalBorder), size[1]-266-(10*self.LocalBorder)), size=(200, 220))

		# 2 Create Button for checking individual batch info per work order
		BatchInfo = wx.Button(self, label="Batch Info",
			pos=(size[0]-575-(10*self.LocalBorder), size[1]-266-(10*self.LocalBorder)), size=(370, 70))

		# 3 Create Button for checking on current WO pallet info
		PalletInfo = wx.Button(self, label="Pallet Info",
			pos=(size[0]-575-(10*self.LocalBorder), size[1]-191-(10*self.LocalBorder)), size=(370, 70))

		# 4 Create Button for checking on Quality Asurance
		QualityAsurance = wx.Button(self, label="Quality Asurance",
			pos=(size[0]-575-(10*self.LocalBorder), size[1]-116-(10*self.LocalBorder)), size=(370, 70))

		#Bind All the Buttons To specific events
		BackButton.Bind(wx.EVT_BUTTON, self.OnBack, )
		BatchInfo.Bind(wx.EVT_BUTTON, self.OnBatchInfo, )
		PalletInfo.Bind(wx.EVT_BUTTON, self.OnPalletInfo, )
		QualityAsurance.Bind(wx.EVT_BUTTON, self.OnQualityAsurance, )
		self.packOff.Bind(wx.EVT_BUTTON, self.OnPackOff, )

		#Turn Shits invisible
		if hideMouse:
			self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			BackButton.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			BatchInfo.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			PalletInfo.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			QualityAsurance.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			self.packOff.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			for header in self._FillSheetProductInfo.keys():
				self._FillSheetProductInfo[header].SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			for header in self._FillSheetWeightsInfo.keys():
				self._FillSheetWeightsInfo[header].SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			for header in self._FillSheetEquipment.keys():
				self._FillSheetEquipment[header].SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

	def CreateDspColumn(self, startingKeys, startingLoc, Button=False, Size=12, Spacers=(10,5), FirstColColor=(255, 255, 255), SecondColColor=(0, 255, 0)):
		curHeaderPos = startingLoc
		curHeaderSpacer = []
		buttonSpacers = []

		#Dictionary Retured for updating pannels latter
		curDspDct = dict()

		#Create Static Text For keepping peace count
		for header,_ in startingKeys:

			curDspDct[header] = None
			subHeader = wx.StaticText(self, -1, header+": ",
				pos =curHeaderPos)

			subHeader.SetFont(wx.Font(Size, wx.SWISS, wx.NORMAL, wx.BOLD))
			ButtonSize = subHeader.GetBestSize()
			subHeader.SetSize(ButtonSize)
			subHeader.SetForegroundColour(FirstColColor) # set text color

			curHeaderPos = (curHeaderPos[0],curHeaderPos[1]+subHeader.GetBestSize()[1]+Spacers[1])

			curHeaderSpacer.append(ButtonSize[0])
			buttonSpacers.append(ButtonSize[1])


		curHeaderPos = (curHeaderPos[0]+max(curHeaderSpacer)+Spacers[0], startingLoc [1])
		ButtonSize = (ButtonSize[0], max(buttonSpacers))
		curHeaderSpacer = []

		for key, text_Spacer in startingKeys:

			if not Button:
				curDspDct[key] = wx.StaticText(self, -1, text_Spacer,
					pos =curHeaderPos)

				curDspDct[key].SetFont(wx.Font(Size, wx.SWISS, wx.NORMAL, wx.BOLD))
				curDspDct[key].SetSize(curDspDct[key].GetBestSize())
				curDspDct[key].SetForegroundColour(SecondColColor) # set text color
				curHeaderSpacer.append(curDspDct[key].GetBestSize()[0])

				curHeaderPos = (curHeaderPos[0], curHeaderPos[1]+curDspDct[key].GetBestSize()[1]+Spacers[1])

			else:
				curDspDct[key]=wx.Button(self, label=text_Spacer,
					pos=curHeaderPos,
					size=ButtonSize)
				curHeaderSpacer.append(ButtonSize[0])

				curHeaderPos = (curHeaderPos[0], curHeaderPos[1]+ButtonSize[1]+Spacers[1])


		return curDspDct , (curHeaderPos[0]+max(curHeaderSpacer), curHeaderPos[1])

	def RefreshData(self):

		current_WO, currentState, currentReason = self.CurrentActivityLogger.getCurrentState()
		WO_StartTime, FillStart, FillEnd = self.CurrentActivityLogger.getStartTimes()

		try:
			self._FillSheetHeaderVariables["Work Order"].SetLabel(current_WO)
		except TypeError:
			self._FillSheetHeaderVariables["Work Order"].SetLabel(str(current_WO))

		self._FillSheetHeaderVariables["Run Start"].SetLabel(WO_StartTime.strftime('%H:%M:%S'))
		self._FillSheetHeaderVariables["Run End"].SetLabel(datetime.datetime.now().strftime('%H:%M:%S'))
		try:
			self._FillSheetHeaderVariables["Fill Start"].SetLabel(FillStart.strftime('%H:%M:%S'))
		except AttributeError:
			self._FillSheetHeaderVariables["Fill Start"].SetLabel(str(FillStart))

		try:
			self._FillSheetHeaderVariables["Fill End"].SetLabel(FillEnd.strftime('%H:%M:%S'))
		except AttributeError:
			self._FillSheetHeaderVariables["Fill End"].SetLabel(str(FillEnd))
		#print self.CurrentActivityLogger.formatDiffDateTime()

		pass

		###############################For reference us only##################################################3
		#self._FillSheetHeaderVariables[("Work Order","######"), ("Run Start","00:00:00"), ("Run End","00:00:00"), ("Fill Start","00:00:00"), ("Fill End","00:00:00")]
		#self._FillSheetWeightsInfo[("Tare Weight(g)","######"), ("Volume(ml)","00:00:00"), ("    Specific Gravity","00:00:00"), ("Weight(g)","00:00:00"), ("Cosmetic","00:00:00")]
		#self._FillSheetProductInfo[("Product Name","######"), ("Formula Ref#","00:00:00"), ("Packing Code","00:00:00")]
		#self.CurrentActivityLogger

	def OnPackOff(self, event=None):
		if 	self.packOff.GetBackgroundColour() == (0,255,0):
			self.packOff.SetBackgroundColour((255,0,0)) # set text color
		else:
			self.packOff.SetBackgroundColour((0,255,0))


	def OnButtonPress(self, event=None):
		theButton = event.GetEventObject()
		theKey = None

		for key in self._FillSheetHeaderVariables.keys():
			if self._FillSheetHeaderVariables[key] == theButton:
				theKey = key

		for key in self._FillSheetWeightsInfo.keys():
			if self._FillSheetWeightsInfo[key] == theButton:
				theKey = key

		for key in self._FillSheetProductInfo.keys():
			if self._FillSheetProductInfo[key] == theButton:
				theKey = key

		for key in self._FillSheetEquipment.keys():
			if self._FillSheetEquipment[key] == theButton:
				theKey = key

		if theKey is not None:
			dlg = NumberInputBox("Input Value", Buttons=["1","2","3","4","5","6","7","8","9","0",".","DEL",])

			if dlg.ShowModal() == wx.ID_OK:
				value = dlg.getDialog()
				dlg.Destroy()

				theButton.SetLabel(value)
				self.CurrentActivityLogger.fillSheet[theKey] = value


	def OnQualityAsurance(self, event=None):
		pass

	def OnBatchInfo(self, event=None):
		pass

	def OnPalletInfo(self, event=None):
		pass

	def OnBack(self, event=None):
		self.parent.TogglFillSheet(event)
