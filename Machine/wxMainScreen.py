"""!/usr/bin/python2.7----------------------------------------------------------
Class that holds the Componets for the main view screen of PQMFG data aquistion system

Written by: Max Seifert AKA cytznx
-------------------------------------------------------------------------------"""

#Gui Elements
import wx
from wxPython.wx import *

#cool stuff
import os, sys
import user

class mainScreenInfoPanel(wx.Panel):
	def __init__(self, parent, frame, size):

		# initialize Pannel
		wx.Panel.__init__(self, parent, size=size)

		#set Background color
		self.SetBackgroundColour("black")

		self.LocalBorder = 5

		# I save this ... for setting size later but i dont think i need to use it...
		self.myParent = parent


		#The Machine Number
		self.MachineNumberHeader = wx.StaticText(self, -1, "##",
			pos =(1*self.LocalBorder,self.LocalBorder))

		#Some Basic formating
		self.MachineNumberHeader.SetFont(wx.Font(40, wx.SWISS, wx.NORMAL, wx.BOLD))
		headerNumberSize = self.MachineNumberHeader.GetBestSize()
		self.MachineNumberHeader.SetSize(headerNumberSize)
		self.MachineNumberHeader.SetForegroundColour((0,255,0)) # set text color
		self.MachineNumberHeader.SetBackgroundColour((0,0,255)) # set text back color

		#Creates the
		mainHeader = wx.StaticText(self, -1, "PQMFG Data Aquision System________________ ",
			pos =((2*self.LocalBorder)+headerNumberSize[0],3.5*self.LocalBorder))

		mainHeader.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
		mainHeader.SetSize(mainHeader.GetBestSize())
		mainHeader.SetForegroundColour((0,255,255)) # set text color
		#mainHeader.SetBackgroundColour((0,0,255)) # set text back color

		startPos = (self.MachineNumberHeader.GetBestSize()[0],self.MachineNumberHeader.GetBestSize()[1]+2*self.LocalBorder)

		"""
		subHeader = wx.StaticText(self, -1, "PQMFG Data Aquision System_______________ ",
			pos =((4*self.LocalBorder)+headerNumberSize[0],3.5*self.LocalBorder))

		subHeader.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
		subHeader.SetSize(mainHeader.GetBestSize())
		subHeader.SetForegroundColour((255,128,0)) # set text color
		"""

		# 1 Create Button for adding BLUR Filter
		#LoadNewWOButton = wx.Button(self, label="Load New WO",
		#	pos=(200, 200), size=(100, 20))
		#
		#LoadNewWOButton.Bind(wx.EVT_BUTTON, self.OnPaint(), )

	def RefreshData(self):
		pass

	def OnPaint(self, evt=None):
		"""set up the device context (DC) for painting"""
		dc = wx.PaintDC(self)
		dc.BeginDrawing()
		dc.SetPen(wx.Pen("red",style=wx.SOLID))
		dc.SetBrush(wx.Brush("red", wx.SOLID))
		# set x, y, w, h for rectangle
		dc.DrawRectangle(self.LocalBorder,self.LocalBorder,200, 200)
		dc.EndDrawing()

class mainScreenButtonPanel(wx.Panel):

		def __init__(self, parent, frame, size,):

			#Tagging Parent
			self.parent = parent
			self.gap = 5

			#some universal variables
			self.button_width = (size[0]-(3*self.gap))/2
			self.button_height = ((int(((2.0/3.0)*(size[1]))-(8*self.gap)))/7)
			self.dialog_width = (size[0])-(3*self.gap)
			self.dialog_height = ((1.0/3.0)*(size[1])) - (3*self.gap)

			self.gap = self.gap

			# Create the Button/Message Panel
			wx.Panel.__init__(self, parent, size=size)

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

			LineDownButton.Bind(wx.EVT_BUTTON, self.SmoothMoreButtonEvent, )


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

		def LoadNewWOButtonEvent(self, event=None):
			pass

		def DeletWOButtonEvent(self, event=None):
			pass

		def AddEmployeeButtonEvent(self, event=None):
			pass

		def LineUpButtonEvent(self, event=None):
			pass

		def CompleteCurrentWOButtonEvent(self, event=None):
			pass

		def AdjustCountButtonEvent(self, event=None):
			pass

		def removeEmployeeButtonEvent(self, event=None):
			pass

		def SmoothMoreButtonEvent(self, event=None):
			pass

		def FillSheetButtonEvent(self, event=None):
			pass

		def SetPrinterButtonEvent(self, event=None):
			pass

		def SetEmailButtonEvent(self, event=None):
			pass

		def UndoFilter(self):
			pass


		def WriteToTextPannel(self, MessageString):
			if(not(MessageString == None)):
				self._messagePannel.AppendText(MessageString)
