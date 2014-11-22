"""!/usr/bin/python2.7----------------------------------------------------------
Third itteration of the Data Aquistion gui(Hopefully the last)

Written by: Max Seifert AKA cytznx
-------------------------------------------------------------------------------"""
import wx, wx.html
import sys

from wxMainScreen import mainScreenButtonPanel
from wxMainScreen import mainScreenInfoPanel

class MainFrame(wx.Frame):
	def __init__(self, title, fps = 30):

		# Gets frame size and stores it
		self.tmpFrameSize = (1366, 768) #wanted to do this dynamically but it was just easier to preset
		self.frameSize = self.tmpFrameSize #wx.GetDisplaySize()

		#Initializes the Extended Frame
		wx.Frame.__init__(self, None, title=title, pos=(0,0), size=self.frameSize,style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

		#Toggle to show or hide FillSheet/MainScreen
		self.showFillsheet = False

		#Sets the currser to what i want
		self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

		# Configure a timer to update the display screen
		self.timer = wx.Timer(self)
		self.timer.Start(1000. / fps)

		#Creates Menu Bar At Top of Screen
		menuBar = wx.MenuBar()

		#Creates Status Bar For Instructions At bottom of Screen
		self.statusbar = self.CreateStatusBar()

		menu = wx.Menu()
		m_exit = menu.Append(wx.ID_EXIT, "E&xit To Terminal\tAlt-X", "Exit To Terminal.")
		m_restart = menu.Append(wx.ID_REDO, "R&estart", "Restart Machine To pull Down new Updates")
		m_shutDown = menu.Append(wx.ID_STOP, "S&hutdown", "Power down the Machine")
		menuBar.Append(menu, "&File")

		#menu = wx.Menu()
		#m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
		#menuBar.Append(menu, "&Help")

		self.SetMenuBar(menuBar)

		#Main Display Screen
		mainDispPanel = wx.Panel(self)

		self.mainButtonPanel = mainScreenButtonPanel(mainDispPanel, self, ((1/3.0)*(self.frameSize[0]-2),self.frameSize[1]-self.statusbar.GetSize()[1]-menuBar.GetSize()[1]))
		self.mainInfoPannel = mainScreenInfoPanel(mainDispPanel, self, ((1/3.0)*(self.frameSize[0]-2),self.frameSize[1]-self.statusbar.GetSize()[1]-menuBar.GetSize()[1]))

		mainDispSizer = wx.BoxSizer(wx.HORIZONTAL)
		mainDispSizer.Add(self.mainInfoPannel,0,wx.EXPAND|wx.ALL,border=2)
		mainDispSizer.Add(self.mainButtonPanel,0,wx.EXPAND|wx.ALL,border=2)

		mainDispPanel.SetSizer(mainDispSizer)

		#Bind Menu Events to Methods
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
		self.Bind(wx.EVT_MENU, self.OnRestart, m_restart)
		self.Bind(wx.EVT_MENU, self.OnShutdown, m_shutDown)

		# This is the timer event that I use to refresh data on the screen
		self.Bind(wx.EVT_TIMER, self.RefreshData)

	def RefreshData(self, event=None):
		self.mainInfoPannel.RefreshData(
			HeaderData=[("Machine Number","11",(255,0,0)),
				("Total Peaces","10501",None),
				("Hourly(Peaces/Minute)","10.02",None)],
			EmployeeList=[])

	def OnClose(self, event):
		dlg = wx.MessageDialog(self,
			"Do you really want to close this application?",
			"Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result == wx.ID_OK:
			self.Destroy()

	def TogglFillSheet(self,event):
		self.showFillsheet = not self.showFillsheet


	def OnShutdown(self, event):
		pass

	def OnRestart(self, event):
		pass


app = wx.App(redirect=False)   # Error messages go to popup window
top = MainFrame("<<project>>")
top.Show()
app.MainLoop()