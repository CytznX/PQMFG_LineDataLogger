# gridEvents.py

import wx
import wx.grid as gridlib

from StateMachine import *

class NumberInputBox(wx.Dialog):
	def __init__(self, outputHeader, Buttons=["1","2","3","4","5","6","7","8","9","0","DEL",], ButtonSize=(75,75)):
		wx.Dialog.__init__(self, None, -1, outputHeader,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
				wx.TAB_TRAVERSAL)

		#Meh Decides what size font i should use
		inputFont = wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD, underline=True,)

		#Create vertical sizer
		vbox = wx.BoxSizer(wx.VERTICAL)

		##########################HEADER LAYER###################################
		pan = wx.Panel(self)
		horizontalBox = wx.BoxSizer(wx.VERTICAL)

		self.Display_Output = wx.TextCtrl(pan, size=(ButtonSize[1]*3, ButtonSize[1]))
		self.Display_Output.SetFont(inputFont)
		horizontalBox.Add(self.Display_Output, 0, wx.ALL, 0)

		pan.SetSizer(horizontalBox) #<---- set sizer of pan to be dial_box
		vbox.Add(pan,wx.ALIGN_CENTER|wx.TOP, border = 4) #<----add pan to main sizer


		##########################BUTTON LAYERS###################################
		pan = wx.Panel(self)
		horizontalBox = wx.BoxSizer(wx.HORIZONTAL)
		count = 1

		for Button in Buttons:
			if count%3 == 0:

				button = wx.Button(pan, label = Button, size = ButtonSize)
				button.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
				button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )
				horizontalBox.Add(button, wx.EXPAND)

				pan.SetSizer(horizontalBox)
				vbox.Add(pan,wx.ALIGN_CENTER|wx.TOP, border = 4) #<----add pan to main sizer

				pan = wx.Panel(self)
				horizontalBox = wx.BoxSizer(wx.HORIZONTAL)
				count = 1

			else:
				button = wx.Button(pan, label = Button, size = ButtonSize)
				button.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
				button.Bind(wx.EVT_BUTTON, self.OnButtonPress, )
				horizontalBox.Add(button, wx.EXPAND)

				count += 1
		if count is not 1:
			pan.SetSizer(horizontalBox)
			vbox.Add(pan,wx.ALIGN_CENTER|wx.TOP, border = 4) #<----add pan to main sizer

		##########################BOTOM LAYERS###################################

		opt_box = wx.BoxSizer(wx.HORIZONTAL)

		opt_close = wx.Button(self, wx.ID_CANCEL, label="Close")
		opt_ok = wx.Button(self, wx.ID_OK,label="OK")

		opt_box.Add(opt_ok)
		opt_box.Add(opt_close, flag =  wx.LEFT, border = 5)
		vbox.Add(opt_box, flag = wx.ALIGN_CENTER|wx.BOTTOM, border = 4)
		self.SetSizer(vbox)
		self.SetMaxSize((ButtonSize[1]*3,400))
		self.SetMinSize((ButtonSize[1]*3,400))
		self.SetSize((ButtonSize[1]*3,400))

	def OnButtonPress(self, event):
		#print "Got: ", event.GetEventObject().GetLabel(), event.GetEventObject().GetLabel() == "DEL"

		if event.GetEventObject().GetLabel() == "DEL":
			self.Display_Output.SetValue(self.Display_Output.GetValue()[:-1])
		else:
			#print "appending: ", event.GetEventObject().GetLabel()
			self.Display_Output.AppendText(event.GetEventObject().GetLabel())

	def OnClose(self, event):
		self.Close(True)

	def getDialog(self):
		return self.Display_Output.GetValue()

class AboutBox(wx.Dialog):
	def __init__(self, InitDictionary):
		wx.Dialog.__init__(self, None, -1, "About <<project>>",
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)

		pan = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)
		dial_box = wx.BoxSizer(wx.HORIZONTAL)
		dial_text = wx.StaticText(pan, label = "Route :")
		dial_text2 = wx.StaticText(pan, label = "Sytle 2: ")
		dial_box.Add(dial_text,0,wx.ALL,20)
		dial_box.Add(dial_text2,0,wx.ALL,5)
		dial_camp = wx.TextCtrl(pan)
		dial_box.Add(dial_camp,wx.EXPAND)
		pan.SetSizer(dial_box) #<---- set sizer of pan to be dial_box

		vbox.Add(pan,wx.ALIGN_CENTER|wx.TOP, border = 4) #<----add pan to main sizer
		opt_box = wx.BoxSizer(wx.HORIZONTAL)
		opt_close = wx.Button(self, label = "Close")
		opt_ok = wx.Button(self, label = "OK" )
		opt_box.Add(opt_ok)
		opt_box.Add(opt_close, flag =  wx.LEFT, border = 5)
		vbox.Add(opt_box, flag = wx.ALIGN_CENTER|wx.BOTTOM, border = 4)
		self.SetSizer(vbox)


########################################################################
class Test(wx.Frame):
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, parent=None, title="An Eventful Grid")

		dlg = NumberInputBox("Input Work Order Number", "Work Order")

		result = dlg.ShowModal()
		if result == wx.ID_OK:
			print "grabbing something: ", dlg.getDialog()
		dlg.Destroy()
		print result

if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = Test().Show()
	app.MainLoop()