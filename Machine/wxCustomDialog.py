# gridEvents.py

import wx
import wx.grid as gridlib
import random
from StateMachine import *

class NumberInputBox(wx.Dialog):
	def __init__(self, outputHeader, Buttons=["1","2","3","4","5","6","7","8","9","0","DEL",], ButtonSize=(75,75),multiLine =False):

		self._ButtonSize = ButtonSize
		self._TxtPannelheight = 100
		self._Border = (5, 5)
		self._NumOfButtonRows = 3

		#The Size of our Dialog Boc
		self._Size = (2*(self._NumOfButtonRows*self._ButtonSize[0]+((self._NumOfButtonRows+1)*self._Border[0])),
			(self._NumOfButtonRows+3)*self._ButtonSize[1]+((self._NumOfButtonRows+3)*self._Border[1]))

		#Creates Dialog FrameWork
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL,
			size=self._Size)

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
	def __init__(self, outputHeader, currentLogger, ButtonSize=(75,75)):

		self._currentLogger = currentLogger
		self._CurrentSelection = []

	def OnButtonPress(self, event):

	def OnClose(self, event):
		self.Close(True)

	def getSelection(self):
		return self._CurrentSelection
########################################################################
class Test(wx.Frame):
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, parent=None, title="An Eventful Grid")

				#Create The ActivityLogger
		self.CurrentActivityLogger = ActivityLogger(rpi=False)

		'''FOR TESTING PURPOSES ONLY'''
		for counter in range(5+int(random.random()*10)):
			self.CurrentActivityLogger.addEmployee(str(100+int(random.random()*50)))
		self.CurrentActivityLogger.addEmployee(str(322))
		self.CurrentActivityLogger.addEmployee(str(3131))
		self.CurrentActivityLogger.addEmployee(str(1441))

		dlg = EmployeeRemoveBox("Input Work Order Number", self.CurrentActivityLogger)

		result = dlg.ShowModal()
		if result == wx.ID_OK:
			print dlg.getDialog().split(", ")
		dlg.Destroy()
		print result

if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = Test().Show()
	app.MainLoop()