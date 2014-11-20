


#Gui Elements
import wx
from wxPython.wx import *

#cool stuff
import os, sys
import user

class mainScreenInfoPanel(wx.Panel):
	def __init__(self, parent, frame):

		# initialize Pannel
		wx.Panel.__init__(self, parent)

		# I save this ... for setting size later but i dont think i need to use it...
		self.myParent = parent

		box = wx.BoxSizer(wx.VERTICAL)

		m_text = wx.StaticText(self, -1, "Hello World!")
		m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text.SetSize(m_text.GetBestSize())
		box.Add(m_text, 0, wx.ALL, 10)

		m_close = wx.Button(self, wx.ID_CLOSE, "Close")
		m_close.Bind(wx.EVT_BUTTON, frame.OnClose)
		box.Add(m_close, 0, wx.ALL, 10)

		self.SetSizer(box)
		self.Layout()

class mainScreenButtonPanel(wx.Panel):

		def __init__(self, parent, frame):

			#Tagging Parent
			self.parent = parent
			self.gap = 5

			self.lastLoadedDirectory = None

			#Variable That counts number of filters applied
			self.filterCounter = 0

			#some universal variables
			self.button_width = 300
			self.button_height = 50
			self.dialog_width = (self.button_width*2)+self.gap
			self.dialog_height = 300



			#Create the Button/Message Panel
			wx.Panel.__init__(self, parent)

			#set Background color
			self.SetBackgroundColour("black")

			#Create Button for adding BLUR Filter
			BlurButton = wx.Button(self, label="Blur",
				pos=(self.gap, self.gap), size=(self.button_width, self.button_height))

			BlurButton.Bind(wx.EVT_BUTTON, self.BlurButtonEvent, )

			#2Create Button for adding CONTOUR Filter
			ContourButton = wx.Button(self, label="Contour",
				pos=(self.gap, 2*self.gap+1*self.button_height), size=(self.button_width, self.button_height))

			ContourButton.Bind(wx.EVT_BUTTON, self.ContourButtonEvent, )

			#3Create Button for adding DETAIL Filter
			DetailButton = wx.Button(self, label="Detail",
				pos=(self.gap, 3*self.gap+2*self.button_height), size=(self.button_width, self.button_height))

			DetailButton.Bind(wx.EVT_BUTTON, self.DetailButtonEvent, )

			#4Create Button for adding EDGE_ENHANCE Filter
			Edge_EnhanceButton = wx.Button(self, label="Edge_Enhance",
				pos=(self.gap, 4*self.gap+3*self.button_height), size=(self.button_width, self.button_height))

			Edge_EnhanceButton.Bind(wx.EVT_BUTTON, self.EdgeEnhanceButtonEvent, )

			#5Create Button for adding EDGE_ENHANCE_MORE Filter
			Edge_Enhance_MoreButton = wx.Button(self, label="Edge_Enhance_More",
				pos=(self.gap, 5*self.gap+4*self.button_height), size=(self.button_width, self.button_height))

			Edge_Enhance_MoreButton.Bind(wx.EVT_BUTTON, self.EdgeEnhanceMoreButtonEvent, )

			#
			########################SECOND COLUM##################################
			#

			#6Create Button for adding EMBOSS Filter
			EmbossButton = wx.Button(self, label="Emboss",
				pos=(2*self.gap + self.button_width, self.gap), size=(self.button_width, self.button_height))

			EmbossButton.Bind(wx.EVT_BUTTON, self.EmbossButtonEvent, )

			#7Create Button for adding FIND_EDGES Filter
			Find_EdgesButton = wx.Button(self, label="Find_Edges",
				pos=(2*self.gap + self.button_width, 2*self.gap+1*self.button_height), size=(self.button_width, self.button_height))

			Find_EdgesButton.Bind(wx.EVT_BUTTON, self.FindEdgesButtonEvent, )

			#8Create Button for adding SMOOTH Filter
			SmoothButton = wx.Button(self, label="Smooth",
				pos=(2*self.gap + self.button_width, 3*self.gap+2*self.button_height), size=(self.button_width, self.button_height))

			SmoothButton.Bind(wx.EVT_BUTTON, self.SmoothButtonEvent, )

			#9Create Button for adding SMOOTH_MORE Filter
			Smooth_MoreButton = wx.Button(self, label="Smooth_More",
				pos=(2*self.gap + self.button_width, 4*self.gap+3*self.button_height), size=(self.button_width, self.button_height))

			Smooth_MoreButton.Bind(wx.EVT_BUTTON, self.SmoothMoreButtonEvent, )

			#10Create Button for adding SHARPEN Filter
			SharpenButton = wx.Button(self, label="Sharpen",
				pos=(2*self.gap + self.button_width, 5*self.gap+4*self.button_height), size=(self.button_width, self.button_height))

			SharpenButton.Bind(wx.EVT_BUTTON, self.SharpenButtonEvent, )

			#11Load Image Button
			LoadImageButton = wx.Button(self, label="Load Image",
				pos=(self.gap, 6*self.gap+5*self.button_height), size=((self.button_width*2)+self.gap, self.button_height))

			LoadImageButton.Bind(wx.EVT_BUTTON, self.LoadImageButtonEvent, )

			#12Load Image Button
			ShowCompImageButton = wx.Button(self, label="Comparison Image",
				pos=(self.gap, 7*self.gap+6*self.button_height), size=((self.button_width*2)+self.gap, self.button_height))

			ShowCompImageButton.Bind(wx.EVT_BUTTON, self.ShowCompImageButtonEvent, )

			#13Reset ImageButton
			ResetImageButton = wx.Button(self, label="Reset Image",
				pos=(self.gap, (8*self.gap)+(7*self.button_height)), size=((self.button_width*2)+self.gap, self.button_height))

			ResetImageButton.Bind(wx.EVT_BUTTON, self.ResetImageButtonEvent, )

			#Create Readout Pannel
			self._messagePannel = wx.TextCtrl( self, -1, pos=(self.gap, (9*self.gap)+(8*self.button_height)),
				size = (self.dialog_width, self.dialog_height),
				style = wx.TE_MULTILINE | wx.TE_READONLY)

		def BlurButtonEvent(self, event=None):
			pass

		def ContourButtonEvent(self, event=None):
			pass

		def DetailButtonEvent(self, event=None):
			pass

		def EdgeEnhanceButtonEvent(self, event=None):
			pass

		def EdgeEnhanceMoreButtonEvent(self, event=None):
			pass

		def EmbossButtonEvent(self, event=None):
			pass

		def FindEdgesButtonEvent(self, event=None):
			pass

		def SmoothButtonEvent(self, event=None):
			pass

		def SmoothMoreButtonEvent(self, event=None):
			pass

		def SharpenButtonEvent(self, event=None):
			pass

		def LoadImageButtonEvent(self, event=None):
			pass

		def ResetImageButtonEvent(self, event=None):
			pass

		def ShowCompImageButtonEvent(self, event=None):
			pass

		def UndoFilter(self):
			pass


		def WriteToTextPannel(self, MessageString):
			if(not(MessageString == None)):
				self._messagePannel.AppendText(MessageString)
