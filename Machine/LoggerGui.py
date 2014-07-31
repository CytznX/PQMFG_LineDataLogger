'''
This is Version 2.0 of the PQMFG Activity Logger Gui Client that displays relevent data from StateMachineV2_0.py and
also provides some user input collection and logging functionality

Created By: Maxwell Seifert

'''

import pygame, pygbutton, sys, os, time
import socket, platform
import random, time, math
import subprocess
import difflib
import platform

from pygame.locals import *
from StateMachine import *
from ScannerReader import BCscanner

#Denotes whats the current FPS that you want the machine to run AT
FPS = 20

#used to calculate the spacing between all the gui objects
BRD_SPACER = 10
TXT_SPACER = 10

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 55

IDSIZE = 105

#Used to Determin window dimensions
WINDOWWIDTH = 1366
WINDOWHEIGHT = 768

#Where the topleft point of text columb is
TEXT_Strt_Top = 20
TEXT_Strt_Left = IDSIZE+3*BRD_SPACER

#Some arbitrary colors I hard codded in
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 51)

DEFAULT_BG = (212, 208, 200)

LIGHT_GREEN = (100, 255, 100)
LIGHT_BLUE = (100, 100, 255)
ORANGE = (255, 128, 0)
MAROON = (150, 0, 0)
DARK_GREEN = (0, 128, 0)
DARK_BLUE = (0, 0, 128)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

#How I shutdown the pi
def shutdownPI():
	command = "/usr/bin/sudo /sbin/shutdown -h now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output


#I thought i was gonna use this method more than i actually did ... so shoot me
def drawText(text, size, color, DisplaySurf, Tx, Ty, Width, Height, SLO, state=None):

	#DisplaySurf = pygame.display.get_surface()
	spacer = 10
	x_pos = Tx+5
	y_pos = Ty+5
	font = pygame.font.Font('freesansbold.ttf', size)

	#This for loop implements some autosizing features
	for t in text:
		x = font.render(t, False, WHITE)

		while x.get_rect()[2] > Width-2*spacer and not size < 10:
			size = size-1
			font = pygame.font.Font('freesansbold.ttf', size)
			x = font.render(t, False, WHITE)

	#here we iterate over all passed text
	for t in text:

		#This if determines what coloring to use... based off state variable
		if state is None:
			x = font.render(t, False, WHITE)
		elif state:

			#Implements basic color scheme (ADD.. I think)
			if not t == '&' and not [item for item in SLO.stillLoggedOn() if t in item or SLO.getName(t) in item]:
				x = font.render(t, False, GREEN)
			elif not t == '&':
				x = font.render(t, False, RED)
			else:
				x = font.render(t, False, WHITE)
		else:

			#Implements basic color scheme (Remove.. I think)
			if not t == '&' and [item for item in SLO.stillLoggedOn() if t in item or SLO.getName(t) in item]:
				x = font.render(t,False,GREEN)
			elif not t == '&':
				x = font.render(t,False,RED)
			else:
				x = font.render(t,False,WHITE)

		#while in for loop If we go beyond the bounds start ne row
		if (x_pos+x.get_rect()[2]> Tx+Width-5) and not size<10:
			x_pos = Tx+5
			y_pos += x.get_rect()[3]+spacer

		#Draw it
		DisplaySurf.blit(x,(x_pos,y_pos))
		x_pos += x.get_rect()[2]+spacer

'''
The Main function
'''
def main():

	#creates the current Activity logger for the line
	cur_AL = ActivityLogger()
	BCreader = BCscanner()

	'''FOR TESTING PURPOSES ONLY'''
	#for counter in range(int(random.random()*50)):
	#	cur_AL.addEmployee(str(100+int(random.random()*100)))

	#Create Some Initialization Variables
	pygame.init()
	FPSCLOCK = pygame.time.Clock()

	#Determines what screen is shown
	GUI_STATE = 0
	PREV_GUI_STATE = 0

	#Keeps track of what display text should be wrote on screen
	displayText = []
	propID = ''
	addRemove = []
	dwnReason = None
	currentMsgDisp = None
	beenClicked = None

	#Sets screen resolution and title
	DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('PQMFG ActivityLogger ')

	#Static Message stings & Deault/header fonts
	#---------------------------------------------------------------------------------------------------
	fontObjectSubscript = pygame.font.Font('freesansbold.ttf',10)
	fontObjectDefault = pygame.font.Font('freesansbold.ttf',16)
	fontObjectHeader = pygame.font.Font('freesansbold.ttf',22)
	fontObjectMN = pygame.font.Font('freesansbold.ttf',75)

	MachinWO_Msg = "Current WO#: "
	MachineStatus_Msg = "Line Status: "
	MachineRunTime_Msg = "WO Run Time: "
	Hour_PPM_MSG = "PPM Over Last Hour:"
	AVG_PPM_MSG = "PPM Over WO Runtime:"

	#Keeps track of col positions for averaging
	messageLengths = []
	dynamicMsgLength = []

	'''
	This I create header messages and general information
	--------------------------------------------------------------------------------------------------------------
	'''
	initStaticText = []
	#HEADER Message
	MachineTag_SO = fontObjectHeader.render("___PQMFG Line Controler_____________________",False, LIGHT_BLUE)
	MachineTag_Rect = MachineTag_SO.get_rect()
	MachineTag_Rect.topleft = (TEXT_Strt_Left,TEXT_Strt_Top)

	initStaticText.append((MachineTag_SO,MachineTag_Rect))

	#CURRENT Work Order message
	MachinCurWO_SO = fontObjectDefault.render(MachinWO_Msg,False, WHITE)
	MachinCurWO_Rect = MachinCurWO_SO.get_rect()
	MachinCurWO_Rect.topleft = (TEXT_Strt_Left+2*TXT_SPACER,MachineTag_Rect[1]+MachineTag_Rect[3]+TXT_SPACER)

	messageLengths.append(MachinCurWO_Rect[0]+MachinCurWO_Rect[2])
	initStaticText.append((MachinCurWO_SO,MachinCurWO_Rect))

	#RunTime
	MachineRun_SO = fontObjectDefault.render(MachineRunTime_Msg,False, WHITE)
	MachineRun_Rect = MachineRun_SO.get_rect()
	MachineRun_Rect.topleft = (TEXT_Strt_Left+2*TXT_SPACER,MachinCurWO_Rect[1]+MachinCurWO_Rect[3])

	messageLengths.append(MachineRun_Rect[0]+MachineRun_Rect[2])
	initStaticText.append((MachineRun_SO,MachineRun_Rect))


	#STATUS message
	MachineStatus_SO = fontObjectDefault.render(MachineStatus_Msg,False, WHITE)
	MachineStatus_Rect = MachineStatus_SO.get_rect()
	MachineStatus_Rect.topleft = (TEXT_Strt_Left+2*TXT_SPACER,MachineRun_Rect[1]+MachineRun_Rect[3])

	messageLengths.append(MachineStatus_Rect[0]+MachineStatus_Rect[2])
	initStaticText.append((MachineStatus_SO,MachineStatus_Rect))

	#PiecesPerMinute Time Message
	Hour_PPM_MSG_SO = fontObjectDefault.render(Hour_PPM_MSG,False, WHITE)
	Hour_PPM_MSG_Rect = Hour_PPM_MSG_SO.get_rect()
	Hour_PPM_MSG_Rect.topleft = (TEXT_Strt_Left+2*TXT_SPACER,MachineStatus_Rect[1]+MachineStatus_Rect[3]+TXT_SPACER)

	messageLengths.append(Hour_PPM_MSG_Rect[0]+Hour_PPM_MSG_Rect[2])
	initStaticText.append((Hour_PPM_MSG_SO,Hour_PPM_MSG_Rect))

	AVG_PPM_MSG_SO = fontObjectDefault.render(AVG_PPM_MSG,False, WHITE)
	AVG_PPM_MSG_Rect = AVG_PPM_MSG_SO.get_rect()
	AVG_PPM_MSG_Rect.topleft = (TEXT_Strt_Left+2*TXT_SPACER,Hour_PPM_MSG_Rect[1]+Hour_PPM_MSG_Rect[3])

	messageLengths.append(AVG_PPM_MSG_Rect[0]+AVG_PPM_MSG_Rect[2])
	initStaticText.append((AVG_PPM_MSG_SO,AVG_PPM_MSG_Rect))

	DynamicStartPos = max(messageLengths)+TXT_SPACER


	#Total, Fail Boxes Static Message
	TotalParts_MSG_SO = fontObjectDefault.render("Total:",False, WHITE)
	TotalParts_MSG_Rect = TotalParts_MSG_SO.get_rect()
	TotalParts_MSG_Rect.topleft = (BRD_SPACER+TXT_SPACER,MachineStatus_Rect[1]+MachineStatus_Rect[3]+TXT_SPACER)

	initStaticText.append((TotalParts_MSG_SO,TotalParts_MSG_Rect))

	TotalBoxs_MSG_SO = fontObjectDefault.render("Boxes:",False, WHITE)
	TotalBoxs_MSG_Rect = TotalBoxs_MSG_SO.get_rect()
	TotalBoxs_MSG_Rect.topleft = (BRD_SPACER+TXT_SPACER,TotalParts_MSG_Rect[1]+TotalParts_MSG_Rect[3])

	initStaticText.append((TotalBoxs_MSG_SO,TotalBoxs_MSG_Rect))

	TotalFail_MSG_SO = fontObjectDefault.render("Fail:",False, WHITE)
	TotalFail_MSG_Rect = TotalFail_MSG_SO.get_rect()
	TotalFail_MSG_Rect.topleft = (BRD_SPACER+TXT_SPACER,TotalBoxs_MSG_Rect[1]+TotalBoxs_MSG_Rect[3])

	initStaticText.append((TotalFail_MSG_SO,TotalFail_MSG_Rect))


	'''
	BELOW IS WHERE I CREATE THE BUTTONS
	--------------------------------------------------------------------------------------------------------------
	'''

	#Main screen buttons
	buttonChangeWO = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 2*BRD_SPACER, BUTTON_WIDTH/2 -(BRD_SPACER/2), BUTTON_HEIGHT), 'ChangeWork Order')
	buttonChangeWO.font = pygame.font.Font('freesansbold.ttf',13)
	buttonChangeWO.bgcolor = YELLOW

	buttonCompleteWO = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH+(BUTTON_WIDTH/2 +(BRD_SPACER/2)), 2*BRD_SPACER, BUTTON_WIDTH/2 -(BRD_SPACER/2), BUTTON_HEIGHT), 'Complete Work Order')
	buttonCompleteWO.font = pygame.font.Font('freesansbold.ttf',13)
	buttonCompleteWO.bgcolor = GREEN

	buttonSetBoxCount = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 3*BRD_SPACER+BUTTON_HEIGHT, BUTTON_WIDTH/2 -(BRD_SPACER/2), BUTTON_HEIGHT), 'Set PPB')
	buttonSetBoxCount.font = fontObjectDefault

	buttonAdjustCount = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH+(BUTTON_WIDTH/2 +(BRD_SPACER/2)), 3*BRD_SPACER+BUTTON_HEIGHT, BUTTON_WIDTH/2 -(BRD_SPACER/2), BUTTON_HEIGHT), 'Adjust Count')
	buttonAdjustCount.font = fontObjectDefault

	buttonAddEmployee = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 5*BRD_SPACER+2*BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT), 'Add Employee(s)')
	buttonAddEmployee.font = fontObjectDefault

	buttonRemoveEmployee = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 6*BRD_SPACER+3*BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT), 'Remove Employee(s)')
	buttonRemoveEmployee.font = fontObjectDefault

	buttonMachineDown = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 9*BRD_SPACER+5*BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT), 'Bring Line Down')
	buttonMachineDown.font = fontObjectDefault

	buttonMachineUp = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 8*BRD_SPACER+4*BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT), 'Bring Line Up')
	buttonMachineUp.font = fontObjectDefault

	FillSheet = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 11*BRD_SPACER+6*BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT), 'Fill Sheet')
	FillSheet.font = fontObjectDefault
	FillSheet.bgcolor = (50,50,255)

	buttonShutdown = pygbutton.PygButton((WINDOWWIDTH-2*BRD_SPACER-BUTTON_WIDTH, 12*BRD_SPACER+7*BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT), 'ShutDown Line Logger')
	buttonShutdown.font = fontObjectDefault
	buttonShutdown.bgcolor = RED

	#Confirm and cancle buttons
	buttonConfirm = pygbutton.PygButton((WINDOWWIDTH/2 - BUTTON_WIDTH-BRD_SPACER, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Confirm')
	buttonConfirm.font = fontObjectDefault
	buttonConfirm.visible = False

	buttonCancle = pygbutton.PygButton((WINDOWWIDTH/2+BRD_SPACER, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Cancel')
	buttonCancle.font = fontObjectDefault
	buttonCancle.visible = False

	#YES and NO buttons
	buttonYes = pygbutton.PygButton((WINDOWWIDTH/2 - BUTTON_WIDTH-BRD_SPACER, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Yes')
	buttonYes.font = fontObjectDefault
	buttonYes.visible = False

	buttonNo = pygbutton.PygButton((WINDOWWIDTH/2+BRD_SPACER, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'No')
	buttonNo.font = fontObjectDefault
	buttonNo.visible = False

	#OK Button
	buttonOk = pygbutton.PygButton((WINDOWWIDTH/2-BUTTON_WIDTH/2, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'OK')
	buttonOk.font = fontObjectDefault
	buttonOk.visible = False

	buttonTotalCount = pygbutton.PygButton(((WINDOWWIDTH/6)-BUTTON_WIDTH/4, 80+WINDOWHEIGHT/2-BUTTON_HEIGHT-BRD_SPACER/2, BUTTON_WIDTH/2, BUTTON_HEIGHT), 'TotalCount')
	buttonTotalCount.font = fontObjectDefault
	buttonTotalCount.bgcolor = GREEN

	buttonBoxCount = pygbutton.PygButton(((WINDOWWIDTH/6)-BUTTON_WIDTH/4, 80+WINDOWHEIGHT/2+BRD_SPACER/2, BUTTON_WIDTH/2, BUTTON_HEIGHT), 'BoxCount')
	buttonBoxCount.font = fontObjectDefault

	#FILL SHEET BUTTONS
	buttonPackOff = pygbutton.PygButton((WINDOWWIDTH/2+int(2.5*BRD_SPACER),5*BRD_SPACER+153, 24, 25), '     ')
	buttonPackOff.font = fontObjectDefault
	buttonPackOff.bgcolor = RED
	buttonPackOff.visible = False

	buttonADD = pygbutton.PygButton((WINDOWWIDTH/2 - BUTTON_WIDTH-BRD_SPACER, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'ADD')
	buttonADD.visible = False

	buttonBack = pygbutton.PygButton((WINDOWWIDTH/2+BRD_SPACER, WINDOWHEIGHT-BUTTON_HEIGHT- 2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Back')
	buttonBack.visible = False

	#Used for displaying storing buttons
	stillLoggedIn = dict()

	#NumPad
	numPadDic =  dict()
	numpadCenter = WINDOWWIDTH/3

	numPadDic['+/-'] = pygbutton.PygButton((numpadCenter -int(1.5*BUTTON_HEIGHT) - BRD_SPACER, WINDOWHEIGHT-2*BUTTON_HEIGHT- 4*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '+/-')
	numPadDic['&'] = pygbutton.PygButton((numpadCenter -int(1.5*BUTTON_HEIGHT) - BRD_SPACER, WINDOWHEIGHT-2*BUTTON_HEIGHT- 4*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '&')
	numPadDic['DEL'] = pygbutton.PygButton((numpadCenter +int(0.5*BUTTON_HEIGHT) + BRD_SPACER, WINDOWHEIGHT-2*BUTTON_HEIGHT- 4*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), 'DEL')
	numPadDic['0'] = pygbutton.PygButton((numpadCenter -int(0.5*BUTTON_HEIGHT) , WINDOWHEIGHT-2*BUTTON_HEIGHT- 4*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '0')
	numPadDic['1'] = pygbutton.PygButton((numpadCenter -int(1.5*BUTTON_HEIGHT) - BRD_SPACER, WINDOWHEIGHT-5*BUTTON_HEIGHT- 7*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '1')
	numPadDic['2'] = pygbutton.PygButton((numpadCenter -int(0.5*BUTTON_HEIGHT), WINDOWHEIGHT-5*BUTTON_HEIGHT- 7*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '2')
	numPadDic['3'] = pygbutton.PygButton((numpadCenter +int(0.5*BUTTON_HEIGHT) + BRD_SPACER, WINDOWHEIGHT-5*BUTTON_HEIGHT- 7*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '3')
	numPadDic['4'] = pygbutton.PygButton((numpadCenter -int(1.5*BUTTON_HEIGHT) - BRD_SPACER, WINDOWHEIGHT-4*BUTTON_HEIGHT- 6*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '4')
	numPadDic['5'] = pygbutton.PygButton((numpadCenter -int(0.5*BUTTON_HEIGHT), WINDOWHEIGHT-4*BUTTON_HEIGHT- 6*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '5')
	numPadDic['6'] = pygbutton.PygButton((numpadCenter +int(0.5*BUTTON_HEIGHT) + BRD_SPACER, WINDOWHEIGHT-4*BUTTON_HEIGHT- 6*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '6')
	numPadDic['7'] = pygbutton.PygButton((numpadCenter -int(1.5*BUTTON_HEIGHT) - BRD_SPACER, WINDOWHEIGHT-3*BUTTON_HEIGHT- 5*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '7')
	numPadDic['8'] = pygbutton.PygButton((numpadCenter-int(0.5*BUTTON_HEIGHT), WINDOWHEIGHT-3*BUTTON_HEIGHT- 5*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '8')
	numPadDic['9'] = pygbutton.PygButton((numpadCenter +int(0.5*BUTTON_HEIGHT) + BRD_SPACER, WINDOWHEIGHT-3*BUTTON_HEIGHT- 5*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '9')

	numPadDic['/'] = pygbutton.PygButton((numpadCenter -(6*int(0.5*BUTTON_HEIGHT)) , WINDOWHEIGHT-4*BUTTON_HEIGHT- 6*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '/')
	numPadDic['-'] = pygbutton.PygButton((numpadCenter -(6*int(0.5*BUTTON_HEIGHT)) , WINDOWHEIGHT-3*BUTTON_HEIGHT- 5*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '-')
	numPadDic['.'] = pygbutton.PygButton((numpadCenter -(6*int(0.5*BUTTON_HEIGHT)) , WINDOWHEIGHT-2*BUTTON_HEIGHT- 4*BRD_SPACER, BUTTON_HEIGHT, BUTTON_HEIGHT), '.')


	#1)Maitenance, 2)Inventory, 3)Quality_Control
	dwnTimeButtons = dict()
	dwnTimeButtons['Maitenance'] = pygbutton.PygButton((WINDOWWIDTH/2-BUTTON_WIDTH/2, WINDOWHEIGHT/2-int(0.5*BUTTON_HEIGHT)-BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Maitenance')
	dwnTimeButtons['Inventory'] = pygbutton.PygButton((WINDOWWIDTH/2-BUTTON_WIDTH/2, WINDOWHEIGHT/2+int(0.5*BUTTON_HEIGHT), BUTTON_WIDTH, BUTTON_HEIGHT), 'Inventory')
	dwnTimeButtons['Quality_Control'] = pygbutton.PygButton((WINDOWWIDTH/2-BUTTON_WIDTH/2, WINDOWHEIGHT/2+int(1.5*BUTTON_HEIGHT)+BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Quality_Control')
	dwnTimeButtons['Break'] = pygbutton.PygButton((WINDOWWIDTH/2-BUTTON_WIDTH/2, WINDOWHEIGHT/2+int(2.5*BUTTON_HEIGHT)+2*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Break')
	dwnTimeButtons['Mid_Cancle'] = pygbutton.PygButton((WINDOWWIDTH/2-BUTTON_WIDTH/2, WINDOWHEIGHT/2+int(3.5*BUTTON_HEIGHT)+3*BRD_SPACER, BUTTON_WIDTH, BUTTON_HEIGHT), 'Cancel')


	#Buttons For Filling Sheet
	fillSheetButtons = dict()
	fillSheetButtons["Product Name"] = pygbutton.PygButton((WINDOWWIDTH/2+int(2.5*BRD_SPACER)+170,5*BRD_SPACER+55, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')
	fillSheetButtons["Formula Ref#"] = pygbutton.PygButton((WINDOWWIDTH/2+int(2.5*BRD_SPACER)+170,5*BRD_SPACER+87, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')
	fillSheetButtons["Exp. Date"] = pygbutton.PygButton((WINDOWWIDTH/2+int(2.5*BRD_SPACER)+170,5*BRD_SPACER+120, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')

	#Blank Space... HAAHAHAHAHAHAH
	fillSheetButtons["Pump#"] = pygbutton.PygButton((WINDOWWIDTH/2+int(2.5*BRD_SPACER)+170,5*BRD_SPACER+217, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')
	fillSheetButtons["Simplex#"] = pygbutton.PygButton((WINDOWWIDTH/2+int(2.5*BRD_SPACER)+170,5*BRD_SPACER+250, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')

	#pos X and pos y
	x, y, yoffset = 205,375, 32

	fillSheetButtons["FD_Tare"] = pygbutton.PygButton((6 *BRD_SPACER+x,y+BRD_SPACER, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')
	fillSheetButtons["FD_Volume"] = pygbutton.PygButton((6 *BRD_SPACER+x,yoffset+y+BRD_SPACER, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')
	fillSheetButtons["FD_Weight"] = pygbutton.PygButton((6 *BRD_SPACER+x,(2*yoffset)+y+BRD_SPACER, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')
	fillSheetButtons["FD_Cosmetic"] = pygbutton.PygButton((6 *BRD_SPACER+x,(3*yoffset)+y+BRD_SPACER, BUTTON_WIDTH-20, BUTTON_HEIGHT/2), 'N/A')


	xpo, ypo = WINDOWWIDTH/2 +100, 375
	fillSheetSwitcherButtons = dict()
	fillSheetSwitcherButtons["Batch Weights"] = pygbutton.PygButton((xpo,ypo, BUTTON_WIDTH*(2/3.0), BUTTON_HEIGHT), 'Batch Weights')
	fillSheetSwitcherButtons["Pallet Info"] = pygbutton.PygButton((xpo,ypo+BUTTON_HEIGHT+BRD_SPACER, BUTTON_WIDTH*(2/3.0), BUTTON_HEIGHT), 'Pallet Info')
	fillSheetSwitcherButtons["QC Samples"] = pygbutton.PygButton((xpo,ypo+(2*(BUTTON_HEIGHT+BRD_SPACER)), BUTTON_WIDTH*(2/3.0), BUTTON_HEIGHT), 'QC Samples')
	fillSheetSwitcherButtons["Back"] = pygbutton.PygButton((xpo+(BUTTON_WIDTH*(2/3.0))+BRD_SPACER,ypo, BUTTON_WIDTH/2, 3*BUTTON_HEIGHT+2*BRD_SPACER), 'Back')
	fillSheetSwitcherButtons["Back"].bgcolor = YELLOW

	#Itterate over button dictionaries and set there visability to False
	for key in dwnTimeButtons.keys():
		dwnTimeButtons[key].font = fontObjectDefault
		dwnTimeButtons[key].visible = False

	for key in numPadDic.keys():
		numPadDic[key].font = fontObjectDefault
		numPadDic[key].visible = False

	for key in fillSheetSwitcherButtons.keys():
		fillSheetSwitcherButtons[key].visible = False

	for key in fillSheetButtons.keys():
		fillSheetButtons[key].bgcolor = BLACK
		fillSheetButtons[key].fgcolor = RED
		fillSheetButtons[key].visible = False

	'''
	----------------------------------------------------------------------------------------------------
	MASS IMPORTANTE!!! : the main loop of death!!!
	----------------------------------------------------------------------------------------------------
	'''
	while True: # main game loop

		#Sets the caption top help identify what the current state is... should change this later
		pygame.display.set_caption('PQMFG ActivityLogger '+str(GUI_STATE))

		'''
		----------------------------------------------------------------------------------------------------
		Here is our event handler, captures all button/key/scanner actions
		----------------------------------------------------------------------------------------------------
		'''
		if not currentMsgDisp == None:
			if (time.time() - currentMsgDisp[1]) > int(currentMsgDisp[2]):
				GUI_STATE = PREV_GUI_STATE
				PREV_GUI_STATE = 0
				currentMsgDisp = None
		else:

			msg = cur_AL.getMessage()
			if not msg == None:
				currentMsgDisp = (msg[0],time.time(), msg[1])
				PREV_GUI_STATE = GUI_STATE
				GUI_STATE = 8

			for event in pygame.event.get(): # event handling loop

				#Captures events and exicutes code relating to SHUTDOWN BUTTON
				buttonShutDownEvent = buttonShutdown.handleEvent(event)
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or ('click' in buttonShutDownEvent and cur_AL.getCurrentState()[0]==None):
					print 'Quiting...'

					try:
						pygame.quit()

					finally:
						print 'Pygame has quit'
						cur_AL.release()
						del(cur_AL)


						print 'Linelogger State Machine has been destroyed...'
						print 'killing Everything!!!'
						#shutdownPI() #used to kill pi
						sys.exit() #used to return to comandLine

				#if any other key is press we add it to our Barcode Reader objecect
				if event.type == KEYDOWN:
					BCreader.add(event.key)

				#check to see if we have any availible strings collected
				scanVal = BCreader.getAvalibleMessage()
				if not scanVal == '' and not scanVal.startswith('#'):

					if GUI_STATE == 2:
						if displayText == []:
							displayText.append(scanVal)
						else:
							displayText[0] = scanVal

					elif GUI_STATE == 3:
						if not displayText == [] and displayText[-1] == '':
							displayText[-1] = scanVal
							displayText+=['&','']
						else:
							displayText.append(scanVal)
							displayText+=['&','']

					elif GUI_STATE == 4:
						tmp = cur_AL.getName(scanVal)
						if tmp in stillLoggedIn.keys():
							if stillLoggedIn[tmp].bgcolor == DEFAULT_BG:
								stillLoggedIn[tmp].bgcolor = GREEN
								addRemove.append(tmp)
							else:
								stillLoggedIn[tmp].bgcolor = DEFAULT_BG

								if tmp in addRemove:
									addRemove.remove(tmp)
					elif GUI_STATE == 6 or GUI_STATE == 5.5:
						displayText = [scanVal]
						scanVal = ''


				elif GUI_STATE ==5 and not scanVal == '':
					if scanVal == '#MAINTENANCE':
						dwnReason = 'Maitenance'
						GUI_STATE = 5.5
					elif scanVal == '#INVENTORY':
						dwnReason = 'Inventory'
						GUI_STATE = 5.5
					elif scanVal == '#QUALITY_CONTROL':
						dwnReason = 'Quality_Control'
						GUI_STATE = 5.5
					elif scanVal == '#CANCEL':
						GUI_STATE = 0

					scanVal = ''


				#Captures events and exicutes code relating to REMOVE PAIN BUTTONS
				#only visible when removing employees
				for key in stillLoggedIn.keys():
					if 'click' in stillLoggedIn[key].handleEvent(event):
						if stillLoggedIn[key].bgcolor == DEFAULT_BG:
							stillLoggedIn[key].bgcolor = GREEN
							addRemove.append(key)
						else:
							stillLoggedIn[key].bgcolor = DEFAULT_BG

							if key in addRemove:
								addRemove.remove(key)


				for key in fillSheetSwitcherButtons.keys():
					if 'click' in fillSheetSwitcherButtons[key].handleEvent(event):
						if fillSheetSwitcherButtons[key].caption == "Back":
							GUI_STATE = 0

						elif fillSheetSwitcherButtons[key].caption == "Batch Weights":
							GUI_STATE = 9.2

						elif fillSheetSwitcherButtons[key].caption == "Pallet Info":
							GUI_STATE = 9.3

						elif fillSheetSwitcherButtons[key].caption == "QC Samples":
							GUI_STATE = 9.4



				for key in fillSheetButtons.keys():
					if 'click' in fillSheetButtons[key].handleEvent(event):
						GUI_STATE = 9.1
						beenClicked = key

				#Captures events and exicutes code relating to NUMPAD BUTTONS
				for key in numPadDic.keys():
					if 'click' in numPadDic[key].handleEvent(event):

						#If its not a special key append to the display text is empty start new entry
						if displayText == [] and not key == '&' and not key == 'DEL' and not key == '+/-' and not GUI_STATE ==7.1:
							displayText.append(key)

						elif GUI_STATE == 7.1 and key == 'DEL':
							propID= propID[:-1]
						elif GUI_STATE == 7.1:
							propID += key

						#If it is special perform corisponding functions
						elif key == '+/-':
							if numPadDic['+/-'].bgcolor == GREEN:
								numPadDic['+/-'].bgcolor = RED
							else:
								numPadDic['+/-'].bgcolor = GREEN
						elif key == '&' and not displayText == []:
							displayText+=[key,'']
						elif key == 'DEL' and not displayText == []:
							displayText[-1]=displayText[-1][:-1]

						#just append current displaytext word
						elif not displayText == []:
							displayText[-1] += key
						else:
							displayText = [key]

				#Captures events and exicutes code relating to DWNTIME BUTTONS
				for key in dwnTimeButtons.keys():
					if 'click' in dwnTimeButtons[key].handleEvent(event):
						if key == 'Mid_Cancle':
							GUI_STATE = 0
						else:
							dwnReason = key
							GUI_STATE = 5.5

				if 'click' in buttonADD.handleEvent(event):
					pass
				if 'click' in buttonBack.handleEvent(event):
					GUI_STATE = 9.0

				buttonTotalCountEvent = buttonTotalCount.handleEvent(event)
				buttonBoxCountEvent = buttonBoxCount.handleEvent(event)
				if 'click' in buttonBoxCountEvent or 'click' in buttonTotalCountEvent:
					tmp1 = buttonTotalCount.bgcolor
					tmp2 = buttonBoxCount.bgcolor
					buttonTotalCount.bgcolor = tmp2
					buttonBoxCount.bgcolor = tmp1

				buttonPackOffEvent = buttonPackOff.handleEvent(event)
				if 'click' in buttonPackOffEvent:

					if buttonPackOff.bgcolor == RED:
						buttonPackOff.bgcolor = GREEN
						buttonPackOff.caption ="  X  "
					else:
						buttonPackOff.bgcolor = RED
						buttonPackOff.caption ="     "

				#Captures events and exicutes code relating to COMPLETE WORK ORDER BUTTONS
				buttonCompleteEvent = buttonCompleteWO.handleEvent(event)
				if ('click' in buttonCompleteEvent or scanVal == '#COMPLETE_WO') and not cur_AL.getCurrentState()[0]==None:
					GUI_STATE = 1

				#Captures events and exicutes code relating to CHANGE WORK ORDER BUTTONS
				buttonChangeEvent = buttonChangeWO.handleEvent(event)
				if 'click' in buttonChangeEvent or scanVal == '#CHANGE_WO':
					GUI_STATE = 2
					displayText = []

				buttonBoxEvent = buttonSetBoxCount.handleEvent(event)
				if ('click' in buttonBoxEvent or scanVal == '#CHANGE_PPB') and not cur_AL.getCurrentState()[0] == None:
					GUI_STATE = 2.5
					displayText = []

				#Captures events and exicutes code relating to ADD EMPLOYEE BUTTONS
				buttonAddEmployeeEvent = buttonAddEmployee.handleEvent(event)
				if 'click' in buttonAddEmployeeEvent or scanVal == '#ADD_EMPLOYEE':
					GUI_STATE = 3
					displayText = []

				#Captures events and exicutes code relating to REMOVE EMPLOYEE BUTTONS
				buttonRemoveEmployeeEvent = buttonRemoveEmployee.handleEvent(event)
				if 'click' in buttonRemoveEmployeeEvent or scanVal == '#REMOVE_EMPLOYEE':

					#Heres where i set height and width of mini buttons for remove screen
					MiniWidth = BUTTON_HEIGHT*2
					MiniHeight = BUTTON_HEIGHT/2

					#gets and calculates some basic displya variables
					whosLoggedIn = cur_AL.stillLoggedOn()
					count = len(whosLoggedIn)
					pannelWidth = math.ceil(math.sqrt(count))
					rowCount = math.floor((WINDOWHEIGHT-(4*BRD_SPACER)-BUTTON_HEIGHT- 150+BRD_SPACER)/(MiniHeight+BRD_SPACER))
					colCount = math.ceil(count/rowCount)

					#Calculate initial x and y POS
					xpos = WINDOWWIDTH/2 - ((colCount/2)*MiniWidth)-((math.floor(colCount/2))*BRD_SPACER)
					ypos = 150+BRD_SPACER

					#Reset Button dictionary
					stillLoggedIn = dict()

					#Loop that populates buttong dictionary
					for emp in whosLoggedIn:
						stillLoggedIn[emp[0]] = pygbutton.PygButton((xpos , ypos, MiniWidth, MiniHeight), emp[0])
						ypos += MiniHeight+BRD_SPACER

						if ypos > WINDOWHEIGHT-(4*BRD_SPACER)-BUTTON_HEIGHT:
							xpos += MiniWidth+BRD_SPACER
							ypos = 150+BRD_SPACER

					#onto the next one!!! (one == state) ... =)
					GUI_STATE = 4

				#Captures events and exicutes code relating to MACHINE DOWN BUTTON
				buttonMachineDownEvent = buttonMachineDown.handleEvent(event)
				if ('click' in buttonMachineDownEvent or scanVal == '#MACHINE_DOWN') and cur_AL.getCurrentState()[1] == True:
					GUI_STATE = 5

				#Captures events and exicutes code relating to MACHINE UP BUTTON
				buttonMachineUpEvent = buttonMachineUp.handleEvent(event)
				if ('click' in buttonMachineUpEvent or scanVal == '#MACHINE_UP') and cur_AL.getCurrentState()[1] == False:
					GUI_STATE = 6

				#Captures events and exicutes code relating to ADJUST COUNT BUTTON
				buttonAdjustCountEvent = buttonAdjustCount.handleEvent(event)
				if 'click' in buttonAdjustCountEvent and not cur_AL.getCurrentState()[0] == None:
					GUI_STATE = 7
					numPadDic['+/-'].bgcolor = GREEN
					displayText =[]

				#Captures events realating to show schedual buttoin
				FillSheetEvent = FillSheet.handleEvent(event)
				if 'click' in FillSheetEvent and not cur_AL.getCurrentState()[0] == None:
					GUI_STATE = 9

				#Captures events and exicutes code relating to CONFIRM BUTTON
				buttonConfirmEvent = buttonConfirm.handleEvent(event)
				if 'click' in buttonConfirmEvent or scanVal == '#CONFIRM':

					#Figure out what state the GUI is currently in and perform the corrisponding opperations
					if GUI_STATE  ==2 and not displayText==[] and not cur_AL.getCurrentState()[0]==displayText[0]:

						#IF this goto that... =P
						if cur_AL.getCurrentState()[0] == None:
							cur_AL.changeCurrentWO(displayText[0])
							displayText=[]
							GUI_STATE = 0
						else:
							GUI_STATE = 2.1

						scanVal = ''

					elif GUI_STATE ==2.5 and not displayText==[]:
							cur_AL.changePeacesPerBox(int(displayText[0]))
							cur_AL.refreshFailCount()
							displayText=[]
							GUI_STATE = 0

					elif GUI_STATE  ==3 and not displayText==[]:

						for inputs in displayText:
							if not (inputs == '&' or inputs == ''):
								addRemove.append(inputs)

						displayText=[]
						GUI_STATE = 3.1
						scanVal = ''

					elif GUI_STATE == 9.1 and not displayText==[]:

						try:
							fillSheetButtons[beenClicked].caption = displayText[0]
							fillSheetButtons[beenClicked].fgcolor = GREEN
						except Exception, e:
							print displayText

						cur_AL.fillSheet[beenClicked]= displayText[0]

						beenClicked = None
						GUI_STATE = 9
						displayText = []
						addRemove = []
						scanVal = ''

					elif GUI_STATE  ==4 and not addRemove==[]:

						displayText=[]
						GUI_STATE = 4.1
						scanVal = ''

					elif GUI_STATE == 7 and not displayText==[]:

						GUI_STATE = 7.1
						scanVal = ''

					elif GUI_STATE == 7.1:

						truth = False

						if not propID == '':
							if buttonTotalCount.bgcolor == GREEN:
								if numPadDic['+/-'].bgcolor == GREEN:
									truth = cur_AL.inc_CurTotalCount(amount = int(displayText[0]), force = True, ID = propID)
									#print "1" , truth, displayText[0], int(displayText[0]), propID
								else:
									truth = cur_AL.inc_CurTotalCount(amount = -1*int(displayText[0]), force = True, ID = propID)
									#print "2" , truth
							else:
								if numPadDic['+/-'].bgcolor == GREEN:
									truth = cur_AL.inc_CurBoxCount(amount = int(displayText[0]), force = True, ID = propID)
									#print "3" , truth
								else:
									truth = cur_AL.inc_CurBoxCount(amount = -1*int(displayText[0]), force = True, ID = propID)
									#print "4" , truth

						if truth:
							GUI_STATE = 0
							propID = ''
							displayText=[]

						else:
							propID=''


					elif not scanVal == '#CONFIRM':
						GUI_STATE = 0
						displayText=[]


				#Captures events and exicutes code relating to CANCLE BUTTON
				buttonCancleEvent = buttonCancle.handleEvent(event)
				if 'click' in buttonCancleEvent or (scanVal == '#CANCEL' and not GUI_STATE ==2.1):

					if GUI_STATE == 9.1:
						beenClicked = None
						GUI_STATE = 9
						displayText = []
						addRemove = []
						scanVal = ''

					else:
						GUI_STATE = 0
						displayText = []
						scanVal = ''

				#Captures events and exicutes code relating to YES BUTTON
				buttonYesEvent = buttonYes.handleEvent(event)
				if 'click' in buttonYesEvent or (scanVal == '#CONFIRM' and (not GUI_STATE ==3.1 or not GUI_STATE ==4.1)):
					if GUI_STATE ==2.1:
						cur_AL.changeCurrentWO(displayText[0])
						displayText=[]
						GUI_STATE = 0
						scanVal = ''

					elif GUI_STATE ==1:
						cur_AL.finishCurrentWO()
						displayText=[]
						GUI_STATE = 0
						scanVal = ''

					elif GUI_STATE == 6:
						if not displayText == []:
							cur_AL.changeState(cur_AL.getName(displayText[-1]))
							displayText = []
							GUI_STATE = 0
							scanVal = ''

					elif GUI_STATE == 5.5:
						if not displayText == [] or dwnReason == None:
							cur_AL.changeState(cur_AL.getName(displayText[-1]), dwnReason)
							displayText = []
							dwnReason = None
							GUI_STATE = 0
							scanVal = ''

					elif not scanVal == '#CONFIRM':
						GUI_STATE = 0
						displayText=[]
						scanVal = ''

				#Captures events and exicutes code relating to NO BUTTON
				buttonNoEvent = buttonNo.handleEvent(event)
				if 'click' in buttonNoEvent or scanVal == '#CANCLE':
					if GUI_STATE ==2.1:
						cur_AL.changeCurrentWO(displayText[0],False)
						displayText=[]
						GUI_STATE = 0
						scanVal = ''

					else:
						GUI_STATE = 0
						displayText = []
						scanVal = ''

				#Captures events and exicutes code relating to OK BUTTON
				buttonOkEvent = buttonOk.handleEvent(event)
				if 'click' in buttonOkEvent or scanVal == '#CONFIRM':
					if GUI_STATE == 3.1:
						for emp in addRemove:
							cur_AL.addEmployee(emp)
						addRemove =[]
						GUI_STATE = 0
						scanVal = ''

					elif GUI_STATE == 4.1:
						for emp in addRemove:
							cur_AL.removeEmployee(emp)
						addRemove = []
						GUI_STATE = 0
						scanVal = ''

					else:
						GUI_STATE = 0
						displayText = []
						addRemove = []
						scanVal = ''

		'''
		BELOW IS WHERE ALL DYNAMIC AND SOME ADAPTIVE STATIC CONTENT GETS CREATED BASE ON CURENT GUI_STATE
		--------------------------------------------------------------------------------------------------------------
		'''
		#Do This First <--- draws backgroud grey
		DISPLAYSURFACE.fill(GREY)

		#reset after previous itteration
		dynamicContent = []
		DyMessageLengths = []
		Stat2MessageLengths = []

		#This is is what determines what gets drawn to screen
		if not GUI_STATE == 0:

			#Kill all buttons that I dont want
			#-------------------------------------------------------
			buttonChangeWO.visible = False #true or flase
			buttonCompleteWO.visible = False
			buttonSetBoxCount.visible = False
			buttonAddEmployee.visible = False
			buttonRemoveEmployee.visible = False
			buttonMachineDown.visible = False
			buttonMachineUp.visible = False
			buttonAdjustCount.visible = False
			buttonShutdown.visible = False
			buttonOk.visible = False
			FillSheet.visible = False
			buttonPackOff.visible = False

			buttonADD.visible = False
			buttonBack.visible = False

			buttonTotalCount.visible = False
			buttonBoxCount.visible = False

			for key in stillLoggedIn.keys():
				stillLoggedIn[key].visible = False

			for key in fillSheetSwitcherButtons.keys():
				fillSheetSwitcherButtons[key].visible = False

			for key in fillSheetButtons.keys():
				fillSheetButtons[key].visible = False
			#-------------------------------------------------------

			#Here is everything that needs numpad
			if GUI_STATE == 2 or GUI_STATE == 2.5 or GUI_STATE ==3 or GUI_STATE ==7 or GUI_STATE == 9.1:

				#Kill all buttons that I dont want
				#-------------------------------------------------------
				buttonYes.visible = False
				buttonNo.visible = False

				for key in dwnTimeButtons.keys():
					dwnTimeButtons[key].visible = False

				#resurect all buttons that I do want
				#-------------------------------------------------------
				for key in numPadDic.keys():
					if (GUI_STATE == 2 or GUI_STATE == 2.5 or GUI_STATE == 7) and key =='&':
						pass
					elif not GUI_STATE == 7 and key =='+/-':
						pass

					elif (not GUI_STATE==9.1) and (key == '/' or key == '-' or key =='.'):
						numPadDic[key].visible = False

					else:
						numPadDic[key].visible = True

				buttonConfirm.visible = True
				buttonCancle.visible = True
				#-------------------------------------------------------

				#Makes BackGround Blue
				pygame.draw.rect(DISPLAYSURFACE, BLUE, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

				#Makes textbox
				screenTopLeftX = numpadCenter+int(1.5*BUTTON_HEIGHT) + 2*BRD_SPACER
				screenTopLeftY = int(WINDOWHEIGHT-5*BUTTON_HEIGHT-7*BRD_SPACER)
				screenWidth =  (2*numpadCenter +int(1.5*BUTTON_HEIGHT) + BRD_SPACER) - screenTopLeftX
				screenHeight = (4*BUTTON_HEIGHT + 3*BRD_SPACER)

				#Draws text area
				pygame.draw.rect(DISPLAYSURFACE, GREY, (screenTopLeftX, screenTopLeftY, screenWidth, screenHeight))
				pygame.draw.rect(DISPLAYSURFACE, DARK_BLUE, (screenTopLeftX+BRD_SPACER, screenTopLeftY+BRD_SPACER, screenWidth-2*BRD_SPACER, screenHeight-2*BRD_SPACER))

				#Figure out what state gui is in and draw the resulting header
				if GUI_STATE == 2:
					Header_SO = pygame.font.Font('freesansbold.ttf',36).render("Please Type Or Scan In New WO#",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*6)

					Header_SO2 = pygame.font.Font('freesansbold.ttf',36).render("Then Press Confirm",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*7+Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					drawText(displayText,25,GREEN,pygame.display.get_surface(), screenTopLeftX+BRD_SPACER, screenTopLeftY+BRD_SPACER, screenWidth-2*BRD_SPACER, screenHeight-2*BRD_SPACER,cur_AL, None)

				elif GUI_STATE == 2.5:
					Header_SO = pygame.font.Font('freesansbold.ttf',36).render("Please Type Or Scan In The Pieces Per Box",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*6)

					Header_SO2 = pygame.font.Font('freesansbold.ttf',36).render("Then Press Confirm",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*7+Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					drawText(displayText,25,GREEN,pygame.display.get_surface(), screenTopLeftX+BRD_SPACER, screenTopLeftY+BRD_SPACER, screenWidth-2*BRD_SPACER, screenHeight-2*BRD_SPACER,cur_AL, None)

				elif GUI_STATE == 3:

					Header_SO = pygame.font.Font('freesansbold.ttf',36).render("Please Type Or Scan In Employee ID to Add",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*6)

					Header_SO2 = pygame.font.Font('freesansbold.ttf',36).render("Then Press Confirm",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*7+Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					drawText(displayText,25,GREEN,pygame.display.get_surface(), screenTopLeftX+BRD_SPACER, screenTopLeftY+BRD_SPACER, screenWidth-2*BRD_SPACER, screenHeight-2*BRD_SPACER,cur_AL,True)


				elif GUI_STATE == 9.1:
					Header_SO = pygame.font.Font('freesansbold.ttf',36).render("Please Type Or Scan In Valid Input",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*6)

					Header_SO2 = pygame.font.Font('freesansbold.ttf',36).render("Then Press Confirm",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*7+Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					drawText(displayText,25,GREEN,pygame.display.get_surface(), screenTopLeftX+BRD_SPACER, screenTopLeftY+BRD_SPACER, screenWidth-2*BRD_SPACER, screenHeight-2*BRD_SPACER,cur_AL,True)

				elif GUI_STATE == 7:

					buttonTotalCount.visible = True
					buttonBoxCount.visible = True

					Header_SO = pygame.font.Font('freesansbold.ttf',36).render("Please Select Vector(+/-) and Type In Amount",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*6)

					Header_SO2 = pygame.font.Font('freesansbold.ttf',36).render("Then Press Confirm",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*7+Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					drawText(displayText,25,GREEN,pygame.display.get_surface(), screenTopLeftX+BRD_SPACER, screenTopLeftY+BRD_SPACER, screenWidth-2*BRD_SPACER, screenHeight-2*BRD_SPACER,cur_AL, None)

			#If we are in remove employee state
			elif GUI_STATE == 4:

				buttonYes.visible = False
				buttonNo.visible = False

				for key in stillLoggedIn.keys():
					stillLoggedIn[key].visible = True

				for key in dwnTimeButtons.keys():
					dwnTimeButtons[key].visible = False

				for key in numPadDic.keys():
					numPadDic[key].visible = False

				buttonConfirm.visible = True
				buttonCancle.visible = True

				#Makes BackGround Blue
				pygame.draw.rect(DISPLAYSURFACE, BLUE, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

				Header_SO = pygame.font.Font('freesansbold.ttf',36).render("Please Select Or Scan In Employee ID to Remove",False, WHITE)
				Header_Rect = Header_SO.get_rect()
				Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*6)

				Header_SO2 = pygame.font.Font('freesansbold.ttf',36).render("Then Press Confirm",False, WHITE)
				Header_Rect2 = Header_SO2.get_rect()
				Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*7+Header_Rect[3])

				pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
				DISPLAYSURFACE.blit(Header_SO,Header_Rect)

				pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect2)
				DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)


			#If in bring machine up or down state
			elif GUI_STATE == 5 or GUI_STATE == 6 or GUI_STATE == 5.5:

				buttonConfirm.visible = False
				buttonCancle.visible = False

				if GUI_STATE == 5:

					#Makes BackGround RED
					pygame.draw.rect(DISPLAYSURFACE, RED, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

					for key in dwnTimeButtons.keys():
						dwnTimeButtons[key].visible = True

					Header_SO = pygame.font.Font('freesansbold.ttf',75).render("BRING LINE DOWN",False, BLACK)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*4)

					Header_SO2 = fontObjectHeader.render("Please select a Reason",False, BLACK)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*5 +Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, RED, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, RED, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					buttonYes.visible = False
					buttonNo.visible = False

					for key in numPadDic.keys():
						numPadDic[key].visible = False

				#else we draw the main screen
				else:

					for key in dwnTimeButtons.keys():
						dwnTimeButtons[key].visible = False

					buttonYes.visible = True
					buttonNo.visible = True

					#Makes BackGround DARK_GREEN
					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

					Header_SO = pygame.font.Font('freesansbold.ttf',75).render("Confirm",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*4)

					Header_SO2 = fontObjectHeader.render("Enter User ID With Key Pad Or Scanner",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*5 +Header_Rect[3])

					if GUI_STATE == 6:
						Header_SO3 = fontObjectHeader.render("Currently Down For: "+cur_AL.getCurrentState()[2],False, BLACK)
						Header_Rect3 = Header_SO3.get_rect()
						Header_Rect3.topleft = (WINDOWWIDTH/2 - Header_Rect3[2]/2,BRD_SPACER+Header_Rect2[1]+Header_Rect2[3])
					else:
						Header_SO3 = fontObjectHeader.render("Bringing Machine Down For:  "+dwnReason,False, BLACK)
						Header_Rect3 = Header_SO3.get_rect()
						Header_Rect3.topleft = (WINDOWWIDTH/2 - Header_Rect3[2]/2,BRD_SPACER+Header_Rect2[1]+Header_Rect2[3])


					if not displayText == []:
						Header_SO4 = pygame.font.Font('freesansbold.ttf',44).render('ID: '+cur_AL.getName(displayText[-1]),False, RED)
						Header_Rect4 = Header_SO4.get_rect()
						Header_Rect4.topleft = (WINDOWWIDTH*2/3 - Header_Rect4[2]/2,WINDOWHEIGHT/2)

					else:
						Header_SO4 = pygame.font.Font('freesansbold.ttf',44).render('ID: <Please Input>',False, RED)
						Header_Rect4 = Header_SO4.get_rect()
						Header_Rect4.topleft = (WINDOWWIDTH*2/3 - Header_Rect4[2]/2,WINDOWHEIGHT/2)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect4)
					DISPLAYSURFACE.blit(Header_SO4,Header_Rect4)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect3)
					DISPLAYSURFACE.blit(Header_SO3,Header_Rect3)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)


					for key in numPadDic.keys():
						numPadDic[key].visible = True

			#Heres where we draw all the mid state pannels
			elif GUI_STATE == 2.1 or GUI_STATE == 1 or GUI_STATE == 3.1 or GUI_STATE == 4.1 or GUI_STATE == 7.1:

				buttonConfirm.visible = False
				buttonCancle.visible = False

				for key in dwnTimeButtons.keys():
					dwnTimeButtons[key].visible = False

				for key in numPadDic.keys():
					numPadDic[key].visible = False

				if GUI_STATE == 2.1:

					buttonYes.visible = True
					buttonNo.visible = True
					buttonOk.visible = False
					#Makes BackGround YELLOW
					pygame.draw.rect(DISPLAYSURFACE, YELLOW, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

					Header_SO = pygame.font.Font('freesansbold.ttf',75).render("!! WARNING !!",False, RED)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*4)

					Header_SO2 = fontObjectHeader.render("WO already running, upload its progress to server?",False, RED)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*5 +Header_Rect[3])

					pygame.draw.rect(DISPLAYSURFACE, YELLOW, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, YELLOW, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)


				elif GUI_STATE == 1:

					buttonYes.visible = True
					buttonNo.visible = True
					buttonOk.visible = False
					#Makes BackGround DARK_GREEN
					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

					Header_SO = pygame.font.Font('freesansbold.ttf',75).render("Confirm",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*4)

					Header_SO2 = fontObjectHeader.render("Are you sure you want to complete run?",False, WHITE)
					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*5 +Header_Rect[3])

					Header_SO3 = fontObjectHeader.render("WO#: "+cur_AL.getCurrentState()[0],False, BLACK)
					Header_Rect3 = Header_SO3.get_rect()
					Header_Rect3.topleft = (WINDOWWIDTH/2 - Header_Rect3[2]/2,BRD_SPACER+Header_Rect2[1]+Header_Rect2[3])

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect3)
					DISPLAYSURFACE.blit(Header_SO3,Header_Rect3)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

				elif GUI_STATE == 3.1 or GUI_STATE == 4.1 or GUI_STATE == 7.1:
					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

					buttonYes.visible = False
					buttonNo.visible = False
					buttonOk.visible = True

					Header_SO = pygame.font.Font('freesansbold.ttf',75).render("Confirm",False, WHITE)
					Header_Rect = Header_SO.get_rect()
					Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*4)

					if GUI_STATE == 3.1:
						Header_SO2 = fontObjectHeader.render("You have sucsessfuly Added the following employees:",False, WHITE)
					elif GUI_STATE == 4.1:
						Header_SO2 = fontObjectHeader.render("You have sucsessfuly Removed the following employees:",False, WHITE)
					elif GUI_STATE == 7.1:

						Header_SO2 = fontObjectHeader.render('You Want '
															+('Add To ' if numPadDic['+/-'].bgcolor == GREEN else 'Subtract From ')
															+('BoxCount' if not buttonTotalCount.bgcolor == GREEN else 'TotalCount'), False, WHITE)

						if not propID == '':
							Header_SO4 = pygame.font.Font('freesansbold.ttf',44).render('ID: '+cur_AL.getName(propID),False, RED)
						else:
							Header_SO4 = pygame.font.Font('freesansbold.ttf',44).render('ID: <Please Input>',False, RED)

						Header_Rect4 = Header_SO4.get_rect()
						Header_Rect4.topleft = (WINDOWWIDTH*2/3 - Header_Rect4[2]/2,WINDOWHEIGHT/2)


						pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect4)
						DISPLAYSURFACE.blit(Header_SO4,Header_Rect4)

						buttonOk.visible = False
						buttonConfirm.visible = True
						buttonCancle.visible = True

						for key in numPadDic.keys():
							if key =='&':
								pass
							elif key =='+/-':
								pass
							else:
								numPadDic[key].visible = True

					Header_Rect2 = Header_SO2.get_rect()
					Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,BRD_SPACER*5 +Header_Rect[3])



					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect2)
					DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

					pygame.draw.rect(DISPLAYSURFACE, DARK_GREEN, Header_Rect)
					DISPLAYSURFACE.blit(Header_SO,Header_Rect)

					y_pos = Header_Rect2[1]+Header_Rect2[3]+BRD_SPACER

					count = 0

					for emp in addRemove:

						if GUI_STATE == 3.1 and not [item for item in cur_AL.stillLoggedOn() if cur_AL.getName(emp) in item]:
							count+=1
							x = fontObjectHeader.render('(+) '+cur_AL.getName(emp),False,BLACK)
							x_pos = WINDOWWIDTH/2-x.get_rect()[2]/2

							pygame.display.get_surface().blit(x,(x_pos,y_pos))
							y_pos += x.get_rect()[3]+BRD_SPACER

						elif GUI_STATE == 4.1 and [item for item in cur_AL.stillLoggedOn() if cur_AL.getName(emp) in item]:
							count+=1
							x = fontObjectHeader.render('(-) '+cur_AL.getName(emp),False,BLACK)
							x_pos = WINDOWWIDTH/2-x.get_rect()[2]/2

							pygame.display.get_surface().blit(x,(x_pos,y_pos))
							y_pos += x.get_rect()[3]+BRD_SPACER

					if count == 0 and not GUI_STATE == 7.1:
						x = fontObjectHeader.render('N/A',False,RED)
						x_pos = WINDOWWIDTH/2-x.get_rect()[2]/2
						pygame.display.get_surface().blit(x,(x_pos,y_pos))

					elif GUI_STATE == 7.1:
						x = fontObjectHeader.render(str(displayText[0])+' Pieces',False,numPadDic['+/-'].bgcolor)
						x_pos = WINDOWWIDTH/2-x.get_rect()[2]/2
						pygame.display.get_surface().blit(x,(x_pos,y_pos))

			elif GUI_STATE == 8:

				pygame.draw.rect(DISPLAYSURFACE, RED, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

				Header_SO = pygame.font.Font('freesansbold.ttf',75).render("<! NOTICE "+str(int(int(currentMsgDisp[2])-(time.time()-currentMsgDisp[1])))+"!>",False, WHITE)
				Header_Rect = Header_SO.get_rect()
				Header_Rect.topleft = (WINDOWWIDTH/2 - Header_Rect[2]/2,BRD_SPACER*4)

				Header_SO2 = fontObjectHeader.render(currentMsgDisp[0],False, BLACK)
				Header_Rect2 = Header_SO2.get_rect()
				Header_Rect2.topleft = (WINDOWWIDTH/2 - Header_Rect2[2]/2,WINDOWHEIGHT/2 - Header_Rect2[3]/2)

				pygame.draw.rect(DISPLAYSURFACE, RED, Header_Rect)
				DISPLAYSURFACE.blit(Header_SO,Header_Rect)

				pygame.draw.rect(DISPLAYSURFACE, RED, Header_Rect2)
				DISPLAYSURFACE.blit(Header_SO2,Header_Rect2)

			elif GUI_STATE == 9:

				col_1_Len = []
				col_2_Len = []

				buttonPackOff.visible = True
				buttonConfirm.visible = False
				buttonCancle.visible = False

				for key in fillSheetButtons.keys():
					fillSheetButtons[key].visible = True

				for key in fillSheetSwitcherButtons.keys():
					fillSheetSwitcherButtons[key].visible = True

				for key in numPadDic.keys():
					numPadDic[key].visible = False

				#<<< Header and Backgroun Info --------------------------------------------------------
				#--------------------------------------------------------------------------------------

				pygame.draw.rect(DISPLAYSURFACE, BLACK, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))

				Header_SO = pygame.font.Font('freesansbold.ttf',50).render("_____PQ Fill Sheet Interface_____",False, LIGHT_BLUE)
				Header_Rect = Header_SO.get_rect()
				Header_Rect.topleft = (WINDOWWIDTH/2-Header_Rect[2]/2,BRD_SPACER*2)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, Header_Rect)
				DISPLAYSURFACE.blit(Header_SO,Header_Rect)

				Header2_SO = pygame.font.Font('freesansbold.ttf',25).render("___Fill Data_______",False, ORANGE)
				Header2_Rect = Header2_SO.get_rect()
				Header2_Rect.topleft = (3 *BRD_SPACER,3*BRD_SPACER+Header_Rect[3]+(WINDOWHEIGHT/2- 6*BRD_SPACER)+25)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, Header2_Rect)
				DISPLAYSURFACE.blit(Header2_SO,Header2_Rect)

				pygame.draw.rect(DISPLAYSURFACE, GREEN, (2 *BRD_SPACER,3*BRD_SPACER+Header_Rect[3],(WINDOWWIDTH/2-int(2.5*BRD_SPACER)),(WINDOWHEIGHT/2- 4*BRD_SPACER)))
				pygame.draw.rect(DISPLAYSURFACE, GREEN, (WINDOWWIDTH/2+int(0.5*BRD_SPACER),3*BRD_SPACER+Header_Rect[3],(WINDOWWIDTH/2-int(2.5*BRD_SPACER)),(WINDOWHEIGHT/2- 4*BRD_SPACER)))
				pygame.draw.rect(DISPLAYSURFACE, BLACK, (3 *BRD_SPACER,4*BRD_SPACER+Header_Rect[3],(WINDOWWIDTH/2-int(4.5*BRD_SPACER)),(WINDOWHEIGHT/2- 6*BRD_SPACER)))
				pygame.draw.rect(DISPLAYSURFACE, BLACK, (WINDOWWIDTH/2+int(1.5*BRD_SPACER),4*BRD_SPACER+Header_Rect[3],(WINDOWWIDTH/2-int(4.5*BRD_SPACER)),(WINDOWHEIGHT/2- 6*BRD_SPACER)))

				#<<< STATIC TEXT FOR GREEN BOX LEFT ---------------------------------------------------
				#--------------------------------------------------------------------------------------

				nWO_SO = pygame.font.Font('freesansbold.ttf',20).render("WO#:",False, WHITE)
				nWO_Rect = nWO_SO.get_rect()
				nWO_Rect.topleft = (4 *BRD_SPACER,5*BRD_SPACER+Header_Rect[3])
				col_1_Len.append(nWO_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nWO_Rect)
				DISPLAYSURFACE.blit(nWO_SO,nWO_Rect)

				nJS_SO = pygame.font.Font('freesansbold.ttf',20).render("Job Start:",False, WHITE)
				nJS_Rect = nJS_SO.get_rect()
				nJS_Rect.topleft = (nWO_Rect[0],nWO_Rect[1]+nWO_Rect[3]+BRD_SPACER)
				col_1_Len.append(nJS_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nJS_Rect)
				DISPLAYSURFACE.blit(nJS_SO,nJS_Rect)

				nJE_SO = pygame.font.Font('freesansbold.ttf',20).render("Job End:",False, WHITE)
				nJE_Rect = nJE_SO.get_rect()
				nJE_Rect.topleft = (nWO_Rect[0],nJS_Rect[1]+nJS_Rect[3]+BRD_SPACER)
				col_1_Len.append(nJE_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nJE_Rect)
				DISPLAYSURFACE.blit(nJE_SO,nJE_Rect)

				nFS_SO = pygame.font.Font('freesansbold.ttf',20).render("Fill Start:",False, WHITE)
				nFS_Rect = nFS_SO.get_rect()
				nFS_Rect.topleft = (nWO_Rect[0],nJE_Rect[1]+nJE_Rect[3]+BRD_SPACER)
				col_1_Len.append(nFS_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nFS_Rect)
				DISPLAYSURFACE.blit(nFS_SO,nFS_Rect)

				nFE_SO = pygame.font.Font('freesansbold.ttf',20).render("Fill End:",False, WHITE)
				nFE_Rect = nFE_SO.get_rect()
				nFE_Rect.topleft = (nWO_Rect[0],nFS_Rect[1]+nFS_Rect[3]+BRD_SPACER)
				col_1_Len.append(nFE_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nFE_Rect)
				DISPLAYSURFACE.blit(nFE_SO,nFE_Rect)

				#<<< STATIC TEXT FOR GREEN BOX RIGHT---------------------------------------------------
				#--------------------------------------------------------------------------------------
				nPN_SO = pygame.font.Font('freesansbold.ttf',20).render("Product Name:",False, WHITE)
				nPN_Rect = nPN_SO.get_rect()
				nPN_Rect.topleft = (WINDOWWIDTH/2+int(2.5*BRD_SPACER),5*BRD_SPACER+Header_Rect[3])
				col_2_Len.append(nPN_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nPN_Rect)
				DISPLAYSURFACE.blit(nPN_SO,nPN_Rect)

				nFR_SO = pygame.font.Font('freesansbold.ttf',20).render("Formula Ref#:",False, WHITE)
				nFR_Rect = nFR_SO.get_rect()
				nFR_Rect.topleft = (nPN_Rect[0],nPN_Rect[1]+nPN_Rect[3]+BRD_SPACER)
				col_2_Len.append(nFR_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nFR_Rect)
				DISPLAYSURFACE.blit(nFR_SO,nFR_Rect)

				nED_SO = pygame.font.Font('freesansbold.ttf',20).render("Exp. Date:",False, WHITE)
				nED_Rect = nED_SO.get_rect()
				nED_Rect.topleft = (nPN_Rect[0],nFR_Rect[1]+nFR_Rect[3]+BRD_SPACER)
				col_2_Len.append(nED_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nED_Rect)
				DISPLAYSURFACE.blit(nED_SO,nED_Rect)

				nPC_SO = pygame.font.Font('freesansbold.ttf',20).render("Packaging Code:",False, WHITE)
				nPC_Rect = nPC_SO.get_rect()
				nPC_Rect.topleft = (nPN_Rect[0],nFR_Rect[1]+nFR_Rect[3]+BRD_SPACER)
				col_2_Len.append(nPC_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nPC_Rect)
				DISPLAYSURFACE.blit(nPC_SO,nPC_Rect)

				nPO_SO = pygame.font.Font('freesansbold.ttf',20).render("Pack-OFF",False, WHITE)
				nPO_Rect = nPO_SO.get_rect()
				nPO_Rect.topleft = (nPN_Rect[0]+30,nPC_Rect[1]+nPC_Rect[3]+BRD_SPACER)
				col_2_Len.append(nPO_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, nPO_Rect)
				DISPLAYSURFACE.blit(nPO_SO,nPO_Rect)

				EquipHeader_SO = pygame.font.Font('freesansbold.ttf',20).render("________Equipment________",False, ORANGE)
				EquipHeader_Rect = EquipHeader_SO.get_rect()
				EquipHeader_Rect.topleft = (nPN_Rect[0],nPO_Rect[1]+nPO_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, EquipHeader_Rect)
				DISPLAYSURFACE.blit(EquipHeader_SO,EquipHeader_Rect)

				EquipPump_SO = pygame.font.Font('freesansbold.ttf',20).render("Pump#:",False, WHITE)
				EquipPump_Rect = EquipPump_SO.get_rect()
				EquipPump_Rect.topleft = (nPN_Rect[0],EquipHeader_Rect[1]+EquipHeader_Rect[3]+BRD_SPACER)
				col_2_Len.append(EquipPump_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, EquipPump_Rect)
				DISPLAYSURFACE.blit(EquipPump_SO,EquipPump_Rect)

				EquipSimplex_SO = pygame.font.Font('freesansbold.ttf',20).render("Simplex#:",False, WHITE)
				EquipSimplex_Rect = EquipSimplex_SO.get_rect()
				EquipSimplex_Rect.topleft = (nPN_Rect[0],EquipPump_Rect[1]+EquipPump_Rect[3]+BRD_SPACER)
				col_2_Len.append(EquipSimplex_Rect[2])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, EquipSimplex_Rect)
				DISPLAYSURFACE.blit(EquipSimplex_SO,EquipSimplex_Rect)

				#<<< DYNAMIC TEXT FOR GREEN BOX LEFT --------------------------------------------------
				#--------------------------------------------------------------------------------------

				workOrder = cur_AL.getCurrentState()[0]

				times = cur_AL.getStartTimes()

				Stime = times[0].strftime('%H:%M:%S')
				Etime = datetime.datetime.now().strftime('%H:%M:%S')

				Ftime = "N/A"
				FEtime = "N/A"
				FtimeColor = RED

				if not times[1] == None:
					Ftime = times[1].strftime('%H:%M:%S')
					FEtime = times[2].strftime('%H:%M:%S')
					FtimeColor = GREEN

				ndWO_SO = pygame.font.Font('freesansbold.ttf',20).render(workOrder,False, GREEN)
				ndWO_Rect = ndWO_SO.get_rect()
				ndWO_Rect.topleft = (5 *BRD_SPACER+max(col_1_Len),5*BRD_SPACER+Header_Rect[3])

				pygame.draw.rect(DISPLAYSURFACE, BLACK, ndWO_Rect)
				DISPLAYSURFACE.blit(ndWO_SO,ndWO_Rect)

				ndJS_SO = pygame.font.Font('freesansbold.ttf',20).render(Stime,False, GREEN)
				ndJS_Rect = ndJS_SO.get_rect()
				ndJS_Rect.topleft = (ndWO_Rect[0],ndWO_Rect[1]+ndWO_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, ndJS_Rect)
				DISPLAYSURFACE.blit(ndJS_SO,ndJS_Rect)

				ndJE_SO = pygame.font.Font('freesansbold.ttf',20).render(Etime,False, GREEN)
				ndJE_Rect = ndJE_SO.get_rect()
				ndJE_Rect.topleft = (ndWO_Rect[0],ndJS_Rect[1]+ndJS_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, ndJE_Rect)
				DISPLAYSURFACE.blit(ndJE_SO,ndJE_Rect)

				ndFS_SO = pygame.font.Font('freesansbold.ttf',20).render(Ftime,False, FtimeColor)
				ndFS_Rect = ndFS_SO.get_rect()
				ndFS_Rect.topleft = (ndWO_Rect[0],ndJE_Rect[1]+ndJE_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, ndFS_Rect)
				DISPLAYSURFACE.blit(ndFS_SO,ndFS_Rect)

				ndFE_SO = pygame.font.Font('freesansbold.ttf',20).render(FEtime,False, FtimeColor)
				ndFE_Rect = ndFE_SO.get_rect()
				ndFE_Rect.topleft = (ndWO_Rect[0],ndFS_Rect[1]+ndFS_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, ndFE_Rect)
				DISPLAYSURFACE.blit(ndFE_SO,ndFE_Rect)

				#<<< LOWER INFO ---- LEATNESS---------------------------------------------------
				#--------------------------------------------------------------------------------------

				yoffness = 2

				cWD_SO = pygame.font.Font('freesansbold.ttf',15).render("Container Tare Weight(g):",False, WHITE)
				cWD_Rect = cWD_SO.get_rect()
				cWD_Rect.topleft = (6 *BRD_SPACER,Header2_Rect[1]+Header2_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, cWD_Rect)
				DISPLAYSURFACE.blit(cWD_SO,cWD_Rect)

				cV_SO = pygame.font.Font('freesansbold.ttf',15).render("Container Volume(ml):",False, WHITE)
				cV_Rect = cV_SO.get_rect()
				cV_Rect.topleft = (cWD_Rect[0],yoffness+cWD_Rect[1]+cWD_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, cV_Rect)
				DISPLAYSURFACE.blit(cV_SO,cV_Rect)

				cW_SO = pygame.font.Font('freesansbold.ttf',15).render("Container Weight(g):",False, WHITE)
				cW_Rect = cW_SO.get_rect()
				cW_Rect.topleft = (cV_Rect[0],(2*yoffness)+cV_Rect[1]+cV_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, cW_Rect)
				DISPLAYSURFACE.blit(cW_SO,cW_Rect)

				cC_SO = pygame.font.Font('freesansbold.ttf',15).render("Container Cosmetic(g):",False, WHITE)
				cC_Rect = cC_SO.get_rect()
				cC_Rect.topleft = (cW_Rect[0],(3*yoffness)+cW_Rect[1]+cW_Rect[3]+BRD_SPACER)

				pygame.draw.rect(DISPLAYSURFACE, BLACK, cC_Rect)
				DISPLAYSURFACE.blit(cC_SO,cC_Rect)

			elif GUI_STATE == 9.2 or GUI_STATE == 9.3 or GUI_STATE == 9.4:

				buttonADD.visible = True
				buttonBack.visible = True

				pygame.draw.rect(DISPLAYSURFACE, BLUE, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER)))
				curdict = None

				startx,starty = 0,0
				columbsFont = pygame.font.Font('freesansbold.ttf',15)


				if GUI_STATE == 9.2:
					Header_SO = pygame.font.Font('freesansbold.ttf',50).render("_____WO Batch Weights_____",False, WHITE)
					curdict = cur_AL.BatchInfo

				elif GUI_STATE == 9.3:
					Header_SO = pygame.font.Font('freesansbold.ttf',50).render("_____WO Pallets_____",False, WHITE)
					curdict = cur_AL.PalletInfo

				elif GUI_STATE == 9.4:
					Header_SO = pygame.font.Font('freesansbold.ttf',50).render("_____WO QC Samples_____",False, WHITE)
					curdict = cur_AL.QCInfo

 				count = 1
				for header in curdict["INIT"]:

					#Used for eyeing allighnment
					#pygame.draw.rect(DISPLAYSURFACE, GREEN, ((count*((WINDOWWIDTH-(BRD_SPACER*2))/(len(curdict["INIT"])+1)))-(BRD_SPACER/2)+BRD_SPACER,0,(BRD_SPACER),(WINDOWHEIGHT)))

					sub_Header_SO = pygame.font.Font('freesansbold.ttf',15).render("_____"+header+"_____",False, ORANGE)
					sub_Header_Rect = sub_Header_SO.get_rect()
					sub_Header_Rect.topleft = ((count*((WINDOWWIDTH-(BRD_SPACER*2))/(len(curdict["INIT"])+1)))-(sub_Header_Rect[2]/2.0),100)

					pygame.draw.rect(DISPLAYSURFACE, BLUE, sub_Header_Rect)
					DISPLAYSURFACE.blit(sub_Header_SO,sub_Header_Rect)

					count+=1

				Header_Rect = Header_SO.get_rect()
				Header_Rect.topleft = (WINDOWWIDTH/2-Header_Rect[2]/2,BRD_SPACER*2)

				pygame.draw.rect(DISPLAYSURFACE, BLUE, Header_Rect)
				DISPLAYSURFACE.blit(Header_SO,Header_Rect)

		else:

			#Kill The buttons here
			#--------------------------------------------------------------
			buttonChangeWO.visible = True #true or flase
			buttonCompleteWO.visible = True
			buttonSetBoxCount.visible = True
			buttonAddEmployee.visible = True
			buttonRemoveEmployee.visible = True
			buttonMachineDown.visible = True
			buttonMachineUp.visible = True
			buttonAdjustCount.visible = True
			buttonShutdown.visible = True
			FillSheet.visible = True

			buttonADD.visible = False
			buttonBack.visible = False

			buttonPackOff.visible = False
			buttonTotalCount.visible = False
			buttonBoxCount.visible = False

			for key in dwnTimeButtons.keys():
				dwnTimeButtons[key].visible = False

			for key in numPadDic.keys():
				numPadDic[key].visible = False

			for key in stillLoggedIn.keys():
				stillLoggedIn[key].visible = False

			for key in fillSheetButtons.keys():
				fillSheetButtons[key].visible = False

			for key in fillSheetSwitcherButtons.keys():
				fillSheetSwitcherButtons[key].visible = False

			buttonConfirm.visible = False
			buttonCancle.visible = False
			buttonYes.visible = False
			buttonNo.visible = False
			buttonOk.visible = False
			#------------------------------------------------------------

			#Makes Background Black
			pygame.draw.rect(DISPLAYSURFACE, BLACK, (BRD_SPACER,BRD_SPACER,(WINDOWWIDTH-2*BRD_SPACER),(WINDOWHEIGHT- 2*BRD_SPACER))) #<--- Overlay Black Text Area

			#Draw Top Left Box
			pygame.draw.rect(DISPLAYSURFACE, GREY, (BRD_SPACER, BRD_SPACER, IDSIZE + BRD_SPACER, ((WINDOWHEIGHT-(2*BRD_SPACER))/6)-2*BRD_SPACER))
			pygame.draw.rect(DISPLAYSURFACE, BLACK, (BRD_SPACER, BRD_SPACER, IDSIZE, ((WINDOWHEIGHT-(2*BRD_SPACER))/6)-3*BRD_SPACER))

			#Machine ID Number (Shown in top left corner)
			if cur_AL.getCurrentState()[1] == None or not cur_AL.getCurrentState()[1]:
				#Paint it Red
				MachineID_SO = fontObjectMN.render(str(cur_AL.getMachineID()),False, RED)
			else:
				#Paint it Green
				MachineID_SO = fontObjectMN.render(str(cur_AL.getMachineID()),False, GREEN)

			#Creates and draws ID Numbers
			MachineID_Rect = MachineID_SO.get_rect()
			MachineID_Rect.topleft = (BRD_SPACER+((IDSIZE/2)-(MachineID_Rect[2]/2)),BRD_SPACER)

			dynamicContent.append((MachineID_SO,MachineID_Rect))

			if not cur_AL.getCurrentState()[1] == None:
				countColor = GREEN
				counts = cur_AL.getCounts()
				total_msg = str(sum(counts[0]))

				if not counts[3] == None:
					box_msg = str(sum(counts[2]))+'('+str(counts[3])+')'
				else:
					box_msg = str(sum(counts[2]))

				fail_msg = str(counts[1])

			else:
				countColor = RED
				total_msg = 'N/A'
				box_msg = 'N/A'
				fail_msg = 'N/A'

			TotalParts_DyMSG_SO = fontObjectDefault.render(total_msg,False, countColor)
			TotalParts_DyMSG_Rect = TotalParts_DyMSG_SO.get_rect()
			TotalParts_DyMSG_Rect.topleft = (TotalBoxs_MSG_Rect[0]+TotalBoxs_MSG_Rect[2]+TXT_SPACER,MachineStatus_Rect[1]+MachineStatus_Rect[3]+TXT_SPACER)

			dynamicContent.append((TotalParts_DyMSG_SO,TotalParts_DyMSG_Rect))

			TotalBoxs_DyMSG_SO = fontObjectDefault.render(box_msg,False, countColor)
			TotalBoxs_DyMSG_Rect = TotalBoxs_MSG_SO.get_rect()
			TotalBoxs_DyMSG_Rect.topleft = (TotalBoxs_MSG_Rect[0]+TotalBoxs_MSG_Rect[2]+TXT_SPACER,TotalParts_MSG_Rect[1]+TotalParts_MSG_Rect[3])

			dynamicContent.append((TotalBoxs_DyMSG_SO,TotalBoxs_DyMSG_Rect))

			TotalFail_DyMSG_SO = fontObjectDefault.render(fail_msg,False, countColor)
			TotalFail_DyMSG_Rect = TotalFail_DyMSG_SO.get_rect()
			TotalFail_DyMSG_Rect.topleft = (TotalBoxs_MSG_Rect[0]+TotalBoxs_MSG_Rect[2]+TXT_SPACER,TotalBoxs_MSG_Rect[1]+TotalBoxs_MSG_Rect[3])

			dynamicContent.append((TotalFail_DyMSG_SO,TotalFail_DyMSG_Rect))



			'''
			HERE IS WHERE I CREATE FIRST ROW DYNAMIC CONTENT
			--------------------------------------------------------------------------------------------------------------
			'''

			curWO, curState, dwnTimeReason = cur_AL.getCurrentState()
			curRunTime = cur_AL.getRunTime()

			HourPPM = (cur_AL.getCurrentRunningPassAvg(True))
			AvgPPM = (cur_AL.getCurrentRunningPassAvg())

			#Determin what the Current work order and runtime messages are...

			if curState == None or not curState:
				DyTxtColor = RED
				curState_msg = 'Line is Down'
			else:
				DyTxtColor = GREEN
				curState_msg = 'Line Is Up'

			if curState == None:
				wo_msg = 'Line Is Idle'
				runTime_msg = 'N/A'
				curState_msg = 'N/A'
				HourPPM_msg = 'N/A'
				AvgPPM = 'N/A'

			else:
				wo_msg = curWO
				HourPPM_msg = "%.2f" %(cur_AL.getCurrentRunningPassAvg(True))
				AvgPPM = "%.2f" %(cur_AL.getCurrentRunningPassAvg())

				runTime_msg=''

				for ttime in curRunTime:
					if ttime <= 9:
						runTime_msg+='0'+str(ttime)
					else:
						runTime_msg+=str(ttime)
					runTime_msg+=':'

				runTime_msg = runTime_msg[:-1]

			#DYNAMIC: Work Order message
			DY_MachinCurWO_SO = fontObjectDefault.render(wo_msg,False, DyTxtColor)
			DY_MachinCurWO_Rect = DY_MachinCurWO_SO.get_rect()
			DY_MachinCurWO_Rect.topleft = (DynamicStartPos,MachineTag_Rect[1]+MachineTag_Rect[3]+TXT_SPACER)

			DyMessageLengths.append(DY_MachinCurWO_Rect[0]+DY_MachinCurWO_Rect[2])
			dynamicContent.append((DY_MachinCurWO_SO,DY_MachinCurWO_Rect))

			#DYNAMIC: RunTime
			DY_MachineRun_SO = fontObjectDefault.render(runTime_msg,False, DyTxtColor)
			DY_MachineRun_Rect = DY_MachineRun_SO.get_rect()
			DY_MachineRun_Rect.topleft = (DynamicStartPos,DY_MachinCurWO_Rect[1]+DY_MachinCurWO_Rect[3])

			#<<<<<<<<<<<<<<<<<<<<<<
			DyMessageLengths.append(DY_MachineRun_Rect[0]+DY_MachineRun_Rect[2])
			dynamicContent.append((DY_MachineRun_SO,DY_MachineRun_Rect))

			#DYNAMIC: STATUS message
			DY_MachineStatus_SO = fontObjectDefault.render(curState_msg,False, DyTxtColor)
			DY_MachineStatus_Rect = DY_MachineStatus_SO.get_rect()
			DY_MachineStatus_Rect.topleft = (DynamicStartPos,DY_MachineRun_Rect[1]+DY_MachineRun_Rect[3])

			DyMessageLengths.append(DY_MachineStatus_Rect[0]+DY_MachineStatus_Rect[2])
			dynamicContent.append((DY_MachineStatus_SO,DY_MachineStatus_Rect))

			#DYNAMIC: PiecesPerMinute Time Message
			DY_Hour_PPM_MSG_SO = fontObjectDefault.render(HourPPM_msg,False, GREEN)
			DY_Hour_PPM_MSG_Rect = DY_Hour_PPM_MSG_SO.get_rect()
			DY_Hour_PPM_MSG_Rect.topleft = (DynamicStartPos,DY_MachineStatus_Rect[1]+DY_MachineStatus_Rect[3]+TXT_SPACER)

			DyMessageLengths.append(DY_Hour_PPM_MSG_Rect[0]+DY_Hour_PPM_MSG_Rect[2])
			dynamicContent.append((DY_Hour_PPM_MSG_SO,DY_Hour_PPM_MSG_Rect))

			DY_AVG_PPM_MSG_SO = fontObjectDefault.render(AvgPPM,False, GREEN)
			DY_AVG_PPM_MSG_Rect = DY_AVG_PPM_MSG_SO.get_rect()
			DY_AVG_PPM_MSG_Rect.topleft = (DynamicStartPos,DY_Hour_PPM_MSG_Rect[1]+DY_Hour_PPM_MSG_Rect[3])

			DyMessageLengths.append(DY_AVG_PPM_MSG_Rect[0]+DY_AVG_PPM_MSG_Rect[2])
			dynamicContent.append((DY_AVG_PPM_MSG_SO,DY_AVG_PPM_MSG_Rect))


			'''
			HERE IS WHERE I CREATE THE SECOND ROW STATIC CONTENT
			--------------------------------------------------------------------------------------------------------------
			'''
			staticR2StartPos = max(DyMessageLengths)+TXT_SPACER

			#Static maintanance downtime totals
			MainDwnTime_SO = fontObjectDefault.render('Maitenance DwnTime:',False, WHITE)
			MainDwnTime_Rect = MainDwnTime_SO.get_rect()
			MainDwnTime_Rect.topleft = (staticR2StartPos,MachineTag_Rect[1]+MachineTag_Rect[3]+TXT_SPACER)

			Stat2MessageLengths.append(MainDwnTime_Rect[0]+MainDwnTime_Rect[2])
			dynamicContent.append((MainDwnTime_SO,MainDwnTime_Rect))

			#Static Inventory down time totals
			InvDwnTime_SO = fontObjectDefault.render('Inventory DwnTime:',False, WHITE)
			InvDwnTime_Rect = InvDwnTime_SO.get_rect()
			InvDwnTime_Rect.topleft = (staticR2StartPos,DY_MachinCurWO_Rect[1]+DY_MachinCurWO_Rect[3])

			Stat2MessageLengths.append(InvDwnTime_Rect[0]+InvDwnTime_Rect[2])
			dynamicContent.append((InvDwnTime_SO,InvDwnTime_Rect))

			#Static Quality control message
			QCDwnTime_SO = fontObjectDefault.render('QualityCon. DwnTime:',False, WHITE)
			QCDwnTime_Rect = QCDwnTime_SO.get_rect()
			QCDwnTime_Rect.topleft = (staticR2StartPos,DY_MachineRun_Rect[1]+DY_MachineRun_Rect[3])

			Stat2MessageLengths.append(QCDwnTime_Rect[0]+QCDwnTime_Rect[2])
			dynamicContent.append((QCDwnTime_SO,QCDwnTime_Rect))

			#Static Break message
			BreakDwnTime_SO = fontObjectDefault.render('Break DwnTime:',False, WHITE)
			BreakDwnTime_Rect = BreakDwnTime_SO.get_rect()
			BreakDwnTime_Rect.topleft = (staticR2StartPos,DY_MachineStatus_Rect[1]+DY_MachineStatus_Rect[3])

			Stat2MessageLengths.append(BreakDwnTime_Rect[0]+BreakDwnTime_Rect[2])
			dynamicContent.append((BreakDwnTime_SO,BreakDwnTime_Rect))

			#static seperator text
			Seperator_SO = fontObjectDefault.render('--------------------------------------------',False, WHITE)
			Seperator_Rect = Seperator_SO.get_rect()
			Seperator_Rect.topleft = (staticR2StartPos,DY_MachineStatus_Rect[1]+DY_MachineStatus_Rect[3]+TXT_SPACER)

			#dynamicContent.append((Seperator_SO,Seperator_Rect))

			#Static totola dwn time msg
			TotalDwnTime_SO = fontObjectDefault.render('Total DwnTime:',False, WHITE)
			TotalDwnTime_Rect = TotalDwnTime_SO.get_rect()
			TotalDwnTime_Rect.topleft = (staticR2StartPos,DY_Hour_PPM_MSG_Rect[1]+DY_Hour_PPM_MSG_Rect[3])

			Stat2MessageLengths.append(TotalDwnTime_Rect[0]+TotalDwnTime_Rect[2])
			dynamicContent.append((TotalDwnTime_SO,TotalDwnTime_Rect))


			'''
			HERE IS WHERE I CREATE THE SECOND ROW STATIC CONTENT
			--------------------------------------------------------------------------------------------------------------
			'''

			dynamicR2StartPos = max(Stat2MessageLengths)+TXT_SPACER

			#Gets and formates Data
			Totals_Maitenance, Totals_Inventory, Totals_Quality_Control, Totals_Break = cur_AL.getDwnTimesTotals()
			TotalDwnTime = cur_AL.formatDiffDateTime(Totals_Maitenance+Totals_Inventory+Totals_Quality_Control+Totals_Break)

			Totals_Maitenance = cur_AL.formatDiffDateTime(Totals_Maitenance)
			Totals_Inventory = cur_AL.formatDiffDateTime(Totals_Inventory)
			Totals_Quality_Control = cur_AL.formatDiffDateTime(Totals_Quality_Control)
			Totals_Break = cur_AL.formatDiffDateTime(Totals_Break)

			Maintainance_msg = ''
			Inventory_msg = ''
			QC_msg = ''
			Break_msg = ''
			TotalDwnTime_msg =''

			for ttime in Totals_Maitenance:
				if ttime <= 9:
					Maintainance_msg+='0'+str(ttime)
				else:
					Maintainance_msg+=str(ttime)
				Maintainance_msg+=':'

			for ttime in Totals_Inventory:
				if ttime <= 9:
					Inventory_msg+='0'+str(ttime)
				else:
					Inventory_msg+=str(ttime)
				Inventory_msg+=':'

			for ttime in Totals_Quality_Control:
				if ttime <= 9:
					QC_msg+='0'+str(ttime)
				else:
					QC_msg+=str(ttime)
				QC_msg+=':'

			for ttime in Totals_Break:
				if ttime <= 9:
					Break_msg+='0'+str(ttime)
				else:
					Break_msg+=str(ttime)
				Break_msg+=':'

			for ttime in TotalDwnTime:
				if ttime <= 9:
					TotalDwnTime_msg+='0'+str(ttime)
				else:
					TotalDwnTime_msg+=str(ttime)
				TotalDwnTime_msg+=':'

			Maintainance_msg = Maintainance_msg[:-1]
			Inventory_msg = Inventory_msg[:-1]
			QC_msg = QC_msg[:-1]
			Break_msg = Break_msg[:-1]
			TotalDwnTime_msg=TotalDwnTime_msg[:-1]


			#Pick a Color any Color
			mainColor = GREEN
			InvColor = GREEN
			QCColor = GREEN
			BreakColor = GREEN
			totalColor = GREEN

			if dwnTimeReason == 'Maitenance':
				mainColor = RED
				totalColor = RED
			elif dwnTimeReason == 'Inventory':
				InvColor = RED
				totalColor = RED
			elif dwnTimeReason == 'Quality_Control':
				QCColor = RED
				totalColor = RED
			elif dwnTimeReason == 'Break':
				BreakColor = RED
				totalColor = RED

			#dynamic maintanance downtime totals
			Dy_MainDwnTime_SO = fontObjectDefault.render(Maintainance_msg,False, mainColor)
			Dy_MainDwnTime_Rect = Dy_MainDwnTime_SO.get_rect()
			Dy_MainDwnTime_Rect.topleft = (dynamicR2StartPos,MachineTag_Rect[1]+MachineTag_Rect[3]+TXT_SPACER)

			dynamicContent.append((Dy_MainDwnTime_SO,Dy_MainDwnTime_Rect))

			#dynamic Inventory down time totals
			Dy_InvDwnTime_SO = fontObjectDefault.render(Inventory_msg,False, InvColor)
			Dy_InvDwnTime_Rect = Dy_InvDwnTime_SO.get_rect()
			Dy_InvDwnTime_Rect.topleft = (dynamicR2StartPos,DY_MachinCurWO_Rect[1]+DY_MachinCurWO_Rect[3])

			dynamicContent.append((Dy_InvDwnTime_SO,Dy_InvDwnTime_Rect))

			#dynamic Quality Control down time totals
			Dy_QCDwnTime_SO = fontObjectDefault.render(QC_msg,False, QCColor)
			Dy_QCDwnTime_Rect = Dy_QCDwnTime_SO.get_rect()
			Dy_QCDwnTime_Rect.topleft = (dynamicR2StartPos,DY_MachineRun_Rect[1]+DY_MachineRun_Rect[3])

			dynamicContent.append((Dy_QCDwnTime_SO,Dy_QCDwnTime_Rect))

			#dynamic Break down time totals
			Dy_BreakDwnTime_SO = fontObjectDefault.render(Break_msg,False, BreakColor)
			Dy_BreakDwnTime_Rect = Dy_BreakDwnTime_SO.get_rect()
			Dy_BreakDwnTime_Rect.topleft = (dynamicR2StartPos,DY_MachineStatus_Rect[1]+DY_MachineStatus_Rect[3])

			dynamicContent.append((Dy_BreakDwnTime_SO,Dy_BreakDwnTime_Rect))

			#Dynamic total dwn time msg
			Dy_TotalDwnTime_SO = fontObjectDefault.render(TotalDwnTime_msg,False, totalColor)
			Dy_TotalDwnTime_Rect = Dy_TotalDwnTime_SO.get_rect()
			Dy_TotalDwnTime_Rect.topleft = (dynamicR2StartPos,DY_Hour_PPM_MSG_Rect[1]+DY_Hour_PPM_MSG_Rect[3])

			dynamicContent.append((Dy_TotalDwnTime_SO,Dy_TotalDwnTime_Rect))
			Stat2MessageLengths.append(Dy_TotalDwnTime_Rect[0]+Dy_TotalDwnTime_Rect[2])

			'''
			BELOW IS WHERE CURRENT STAFF GET READ IN AND PLACE ON SCREEN
			--------------------------------------------------------------------------------------------------------------
			'''

			count = len(cur_AL.stillLoggedOn())
			staffGap = 10
			colWidth = []
			colHeight = []
			positions = [('Line_Leader',DARK_GREEN), ('Mechanic',MAROON), ('Line_Worker', BLUE)]

			if count>9:
				CStaffTag_SO = fontObjectHeader.render("____________Current Staff Logged-On_("+str(count)+")________________",False, ORANGE)
			else:
				CStaffTag_SO = fontObjectHeader.render("____________Current Staff Logged-On_("+str(count)+")_________________",False, ORANGE)
			CStaffTag_Rect = MachineTag_SO.get_rect()
			CStaffTag_Rect.topleft = (2*BRD_SPACER,175)

			dynamicContent.append((CStaffTag_SO,CStaffTag_Rect))

			Pos = CStaffTag_Rect[0]+TXT_SPACER, CStaffTag_Rect[1] + CStaffTag_Rect[3]+TXT_SPACER

			for position,curColor in positions:
				for staff in cur_AL.stillLoggedOn():
					if staff[1]== position:

						StaffN_SO = fontObjectDefault.render(staff[0]+':',False, WHITE)
						StaffN_Rect = StaffN_SO.get_rect()
						StaffN_Rect.topleft = (Pos[0], Pos[1])

						StaffID_SO = fontObjectDefault.render(position,False, curColor)
						StaffID_Rect = StaffID_SO.get_rect()
						StaffID_Rect.topleft = (StaffN_Rect[0]+StaffN_Rect[2]+staffGap,Pos[1])

						dynamicContent.append((StaffN_SO,StaffN_Rect))
						dynamicContent.append((StaffID_SO,StaffID_Rect))

						curHeight = max([StaffID_Rect[3],StaffN_Rect[3]])

						colWidth.append((StaffID_Rect[0]+StaffID_Rect[2])-StaffN_Rect[0])
						colHeight.append(curHeight)

						count+=1

						if Pos[1]+(2*curHeight) > WINDOWHEIGHT-10:
							Pos = 2*staffGap+Pos[0]+max(colWidth), CStaffTag_Rect[1] + CStaffTag_Rect[3] +TXT_SPACER
							colWidth = []
							colHeight = []
						else:
							Pos = Pos[0],Pos[1]+curHeight

			'''
			HERE IS WHERE I DRAW BOTH STATIC & DYNAMIC CONTENT
			--------------------------------------------------------------------------------------------------------------
			'''

			#Draws everything in initstatictext
			for SO,Rect in initStaticText:
				pygame.draw.rect(DISPLAYSURFACE, BLACK, Rect)
				DISPLAYSURFACE.blit(SO,Rect)

			for SO,Rect in dynamicContent:
				pygame.draw.rect(DISPLAYSURFACE, BLACK, Rect)
				DISPLAYSURFACE.blit(SO,Rect)


		#we always draw buttons because visibility is a method function handled in the events
		buttonCompleteWO.draw(DISPLAYSURFACE)
		buttonChangeWO.draw(DISPLAYSURFACE)
		buttonSetBoxCount.draw(DISPLAYSURFACE)
		buttonAddEmployee.draw(DISPLAYSURFACE)
		buttonRemoveEmployee.draw(DISPLAYSURFACE)
		buttonMachineDown.draw(DISPLAYSURFACE)
		buttonMachineUp.draw(DISPLAYSURFACE)
		buttonAdjustCount.draw(DISPLAYSURFACE)
		buttonShutdown.draw(DISPLAYSURFACE)
		buttonConfirm.draw(DISPLAYSURFACE)
		buttonCancle.draw(DISPLAYSURFACE)
		buttonYes.draw(DISPLAYSURFACE)
		buttonNo.draw(DISPLAYSURFACE)
		buttonOk.draw(DISPLAYSURFACE)
		buttonTotalCount.draw(DISPLAYSURFACE)
		buttonBoxCount.draw(DISPLAYSURFACE)
		FillSheet.draw(DISPLAYSURFACE)
		buttonPackOff.draw(DISPLAYSURFACE)
		buttonADD.draw(DISPLAYSURFACE)
		buttonBack.draw(DISPLAYSURFACE)

		#only for remove pane
		for key in stillLoggedIn.keys():
			stillLoggedIn[key].draw(DISPLAYSURFACE)

		#Only for bring machine down pain
		for key in dwnTimeButtons.keys():
			dwnTimeButtons[key].draw(DISPLAYSURFACE)

		for key in fillSheetButtons.keys():
			fillSheetButtons[key].draw(DISPLAYSURFACE)

		for key in fillSheetSwitcherButtons.keys():
			fillSheetSwitcherButtons[key].draw(DISPLAYSURFACE)

		#Draw numpad
		for key in numPadDic.keys():
			numPadDic[key].draw(DISPLAYSURFACE)

		pygame.display.update()
		FPSCLOCK.tick(FPS)


if __name__ == '__main__':
	main()
