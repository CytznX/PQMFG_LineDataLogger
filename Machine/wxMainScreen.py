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

		box = wx.BoxSizer(wx.VERTICAL)

		m_text = wx.StaticText(self, -1, "___PQMFG Data Aquision System____________________________")
		m_text.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text.SetSize(m_text.GetBestSize())
		box.Add(m_text, 0, wx.ALL, 10)

		m_close = wx.Button(self, wx.ID_CLOSE, "Close")
		m_close.Bind(wx.EVT_BUTTON, frame.OnClose)
		box.Add(m_close, 0, wx.ALL, 10)

		self.SetSizer(box)
		self.Layout()

	def RefreshData(self):
		pass


class mainScreenButtonPanel(wx.Panel):

		def __init__(self, parent, frame, size,):

			#Tagging Parent
			self.parent = parent
			self.gap = 5

			#some universal variables
			self.button_width = (size[0]-(3*self.gap))/2
			self.button_height = ((int(((2.0/3.0)*(size[1]))-(8*self.gap)))/7)
			self.dialog_width = (size[0])-(3*self.gap)
			self.dialog_height = ((1.0/3.0)*(size[1])) - (2*self.gap)

			self.gap = self.gap

			# Create the Button/Message Panel
			wx.Panel.__init__(self, parent, size=size)

			# set Background color
			self.SetBackgroundColour("black")

			# 1 Create Button for adding BLUR Filter
			LoadNewWOButton = wx.Button(self, label="Load New WO",
				pos=(self.gap, self.gap), size=(self.button_width, self.button_height))

			LoadNewWOButton.Bind(wx.EVT_BUTTON, self.LoadNewWOButtonEvent, )

			# 2 Create Button for adding CONTOUR Filter
			DeletWOButton = wx.Button(self, label="Delete Current WO",
				pos=(self.gap, 2*self.gap+1*self.button_height),
				size=(self.button_width, self.button_height))

			DeletWOButton.Bind(wx.EVT_BUTTON, self.DeletWOButtonEvent, )

			# 3 Create Button for adding DETAIL Filter
			AddEmployeeButton = wx.Button(self, label="Add Employee",
				pos=(self.gap, 3*self.gap+2*self.button_height),
				size=(self.button_width, self.button_height))

			AddEmployeeButton.Bind(wx.EVT_BUTTON, self.AddEmployeeButtonEvent, )

			# 4 Create Button for adding EDGE_ENHANCE Filter
			LineUpButton = wx.Button(self, label="Bring Line Up",
				pos=(self.gap, 4*self.gap+3*self.button_height),
				size=(self.button_width, self.button_height))

			LineUpButton.Bind(wx.EVT_BUTTON, self.LineUpButtonEvent, )

			#
			########################SECOND COLUM##################################
			#

			# 5 Create Button for adding EMBOSS Filter
			CompleteCurrentWOButton = wx.Button(self, label="Complete Current WO",
				pos=(2*self.gap + self.button_width, self.gap),
				size=(self.button_width, self.button_height))

			CompleteCurrentWOButton.Bind(wx.EVT_BUTTON, self.CompleteCurrentWOButtonEvent, )

			# 6 Create Button for adding FIND_EDGES Filter
			AdjustCountButton = wx.Button(self, label="Adjust Current Count",
				pos=(2*self.gap + self.button_width, 2*self.gap+1*self.button_height),
				size=(self.button_width, self.button_height))

			AdjustCountButton.Bind(wx.EVT_BUTTON, self.AdjustCountButtonEvent, )

			# 7 Create Button for adding SMOOTH Filter
			removeEmployeeButton = wx.Button(self, label="Remove Employee",
				pos=(2*self.gap + self.button_width, 3*self.gap+2*self.button_height),
				size=(self.button_width, self.button_height))

			removeEmployeeButton.Bind(wx.EVT_BUTTON, self.removeEmployeeButtonEvent, )

			# 8 Create Button for adding SMOOTH_MORE Filter
			LineDownButton = wx.Button(self, label="Bring Line Down",
				pos=(2*self.gap + self.button_width, 4*self.gap+3*self.button_height),
				size=(self.button_width, self.button_height))

			LineDownButton.Bind(wx.EVT_BUTTON, self.SmoothMoreButtonEvent, )


			#
			########################Bottom Row##################################
			#

			# 11 Load Image Button
			FillSheetButton = wx.Button(self, label="Fill Sheet",
				pos=(self.gap, 5*self.gap+4*self.button_height),
				size=((self.button_width*2)+self.gap, self.button_height))

			FillSheetButton.Bind(wx.EVT_BUTTON, self.FillSheetButtonEvent, )

			# 12 Load Image Button
			SetEmailButton = wx.Button(self, label="Set Email Updates",
				pos=(self.gap, 6*self.gap+5*self.button_height),
				size=((self.button_width*2)+self.gap, self.button_height))

			SetEmailButton.Bind(wx.EVT_BUTTON, self.SetEmailButtonEvent, )

			# 13 Reset ImageButton
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
