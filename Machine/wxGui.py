"""!/usr/bin/python2.7----------------------------------------------------------
Third itteration of the Data Aquistion gui(Hopefully the last)

Written by: Max Seifert AKA cytznx
-------------------------------------------------------------------------------"""
import wx, wx.html
import sys
import subprocess

from wxMainScreen import mainScreenButtonPanel
from wxMainScreen import mainScreenInfoPanel
from wxFillScreen import fillScreenInfoPanel
from wxCustomDialog import NumberInputBox
from StateMachine import *

class MainFrame(wx.Frame):
	def __init__(self, title, hideMouse=False, fps = 5):

		#Create The ActivityLogger
		self.CurrentActivityLogger = ActivityLogger(rpi=False)

		'''FOR TESTING PURPOSES ONLY'''
		#for counter in range(int(random.random()*50)):
		#	cur_AL.addEmployee(str(100+int(random.random()*100)))

		# Gets frame size and stores it
		self.tmpFrameSize = (1366, 768) #wanted to do this dynamically but it was just easier to preset
		self.frameSize = self.tmpFrameSize #wx.GetDisplaySize()

		#Initializes the Extended Frame
		wx.Frame.__init__(self, None, title=title, pos=(0,0), size=self.frameSize,style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

		# Configure a timer to update the display screen
		self.timer = wx.Timer(self)
		self.timer.Start(1000. / fps)

		#Creates Menu Bar At Top of Screen
		self.menuBar = wx.MenuBar()

		#Creates Status Bar For Instructions At bottom of Screen
		self.statusbar = self.CreateStatusBar()

		menu = wx.Menu()
		m_exit = menu.Append(wx.ID_EXIT, "E&xit To Terminal\tAlt-X", "Exit To Terminal.")
		m_restart = menu.Append(wx.ID_REDO, "R&estart", "Restart Machine To pull Down new Updates")
		m_shutDown = menu.Append(wx.ID_STOP, "S&hutdown", "Power down the Machine")
		self.menuBar.Append(menu, "&File")

		#menu = wx.Menu()
		#m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
		#menuBar.Append(menu, "&Help")

		self.SetMenuBar(self.menuBar)

		#Main Display Screen
		self.mainDispPanel = wx.Panel(self)

		self.mainButtonPanel = mainScreenButtonPanel(self.mainDispPanel, self, self.CurrentActivityLogger, hideMouse, ((1/3.0)*(self.frameSize[0]-2),self.frameSize[1]-self.statusbar.GetSize()[1]-self.menuBar.GetSize()[1]))
		self.mainInfoPannel = mainScreenInfoPanel(self.mainDispPanel, self,self.CurrentActivityLogger, hideMouse, ((1/3.0)*(self.frameSize[0]-2),self.frameSize[1]-self.statusbar.GetSize()[1]-self.menuBar.GetSize()[1]))

		self.fillScreenPannel = fillScreenInfoPanel(self, self.CurrentActivityLogger, hideMouse, ((self.frameSize[0]-2),self.frameSize[1]-self.statusbar.GetSize()[1]-self.menuBar.GetSize()[1]))
		self.fillScreenPannel.Hide()

		mainDispSizer = wx.BoxSizer(wx.HORIZONTAL)
		mainDispSizer.Add(self.mainInfoPannel,0,wx.EXPAND|wx.ALL,border=2)
		mainDispSizer.Add(self.mainButtonPanel,0,wx.EXPAND|wx.ALL,border=2)

		self.mainDispPanel.SetSizer(mainDispSizer)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.mainDispPanel, 1, wx.EXPAND)
		self.sizer.Add(self.fillScreenPannel, 1, wx.EXPAND)
		self.SetSizer(self.sizer)

		#Bind Menu Events to Methods
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
		self.Bind(wx.EVT_MENU, self.OnRestart, m_restart)
		self.Bind(wx.EVT_MENU, self.OnShutdown, m_shutDown)

		# This is the timer event that I use to refresh data on the screen
		self.Bind(wx.EVT_TIMER, self.RefreshData)

		#Hides the currser on all pannels
		if hideMouse:
			self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			self.statusbar.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			self.menuBar.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

			self.mainDispPanel.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			self.mainButtonPanel.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
			self.mainInfoPannel.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))


	def RefreshData(self, event=None):
		if self.mainDispPanel.IsShown():
			self.mainInfoPannel.RefreshData()
		else:
			self.fillScreenPannel.RefreshData()


	def OnClose(self, event):

		#Gets the current state of the Machine and passes to to msg select
		current_WO, currentState, currentReason = self.CurrentActivityLogger.getCurrentState()

		#If theres no current workorer running
		if current_WO is None:

			#Ask iif you want to quit
			dlg = wx.MessageDialog(self,
				"Do you really want to close this application?",
				"Confirm Exit", wx.YES_NO |wx.ICON_QUESTION)
			result = dlg.ShowModal()
			dlg.Destroy()

			#If selection was yes ... bail out
			if result == wx.ID_YES:

				print "Releasing Current Logger"
				self.CurrentActivityLogger.release()
				print "Deleting Current Logger"
				del(self.CurrentActivityLogger)
				print "Logger Destroyed"
				self.Destroy()

		#Else the tell them they need complete the Work Order
		else:
			dlg = wx.MessageDialog(self, "Cannot Exit Without Completeing Work Order: "+current_WO, "Warning WO Still Running", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()

	def TogglFillSheet(self,event):

		if self.mainDispPanel.IsShown():
			self.mainDispPanel.Hide()
			self.fillScreenPannel.Show()
		else:
			self.mainDispPanel.Show()
			self.fillScreenPannel.Hide()
		self.Layout()

	#How I shutdown the pi
	def shutdownPI(self):
		command = "/usr/bin/sudo /sbin/shutdown -h now"
		process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
		output = process.communicate()[0]
		print output

	def OnShutdown(self, event):
		pass

	def OnRestart(self, event):
		pass


app = wx.App(redirect=False)   # Error messages go to popup window
top = MainFrame("PQMFG Data Aquisition System")
top.Show()
app.MainLoop()