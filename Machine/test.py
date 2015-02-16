from StateMachine import ActivityLogger
import time
import random

import re
import MySQLdb
import _mysql
import datetime


import sys
"""
result = None
try:
	con = _mysql.connect("192.168.20.31","cyrus","cyrus2sql","pqmfg_daq")

	con.query("SELECT VERSION()")
	result = con.use_result()

except _mysql.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	sys.exit(1)

else:
		print "MySQL version: %s" % result.fetch_row()[0]

finally:
	if con:
		con.close()

---------------------------------------------------------------------

_machineVars = {"WO": self.current_WO,
								"Bulk Wo" : self.isBulk,
								"Time Log Created" : datetime.datetime.now(),
								"Machine ID": self.MachineID,
								"WO StartTime": self.WO_StartTime,
								"Total Count": self.totalCount,
								"Fail Count": self.failCount,
								"Box Count": self.boxCount,
								"Peaces Per Box": self.peacesPerBox,
								"Fill Start": self.FillStart,
								"Fill End": self.FillEnd,
								"Line Var Adjustments": self.adjustments,
								"Maintanance Down Times": self.MaintananceDwnTime,
								"Inventory Down Time": self.InventoryDwnTime,
								"Quality Control Down Time": self.QualityControlDwnTime,
								"Break Down Time": self.BreakDownTime,
								"ChangeOver Time": self.ChangeOverTime}

_dwntime = self.getDwnTimesTotals()
_dwnTimes = {"FormattedTotal": self.formatDiffDateTime(sum(_dwntime)),
							"FormattedMain": self.formatDiffDateTime(_dwntime[0]),
							"FormattedInv": self.formatDiffDateTime(_dwntime[1]),
							"FormattedQuality": self.formatDiffDateTime(_dwntime[2]),
							"FormattedBreak": self.formatDiffDateTime(_dwntime[3]),
							"FormattedChngOvr": self.formatDiffDateTime(_dwntime[4])}


log = (_machineVars, self.EmpWorkingDic, _dwnTimes, self.fillSheet,
				self._BatchInfo, self._PalletInfo, self._QCInfo)


---------------------------------------------------------------------"""


CurrentActivityLogger = ActivityLogger(rpi=False)

for counter in range(5+int(random.random()*10)):
	CurrentActivityLogger.addEmployee(str(100+int(random.random()*50)))
CurrentActivityLogger.addEmployee(str(322))
CurrentActivityLogger.addEmployee(str(3131))
CurrentActivityLogger.addEmployee(str(1441))

#UpFrom Change over
CurrentActivityLogger.changeCurrentWO(666)
time.sleep(2)
CurrentActivityLogger.changeState(000)

#1) Maitenance, 2) Inventory, 3) Quality_Control 4) Break
CurrentActivityLogger.changeState(322, "Maitenance")
time.sleep(3)
CurrentActivityLogger.changeState(322)
CurrentActivityLogger.changeState(322, "Inventory")
time.sleep(3)
CurrentActivityLogger.changeState(322)
CurrentActivityLogger.changeState(322, "Quality_Control")
time.sleep(3)
CurrentActivityLogger.changeState(322)
CurrentActivityLogger.changeState(322, "Break")
time.sleep(3)
CurrentActivityLogger.changeState(322)

# "Weight(g)" or "Volume(ml)" and "    Specific Gravity"
CurrentActivityLogger.fillSheet["Volume(ml)"] = 10
CurrentActivityLogger.fillSheet["    Specific Gravity"] = 10
CurrentActivityLogger.fillSheet["Cosmetic"] = 0.5
CurrentActivityLogger.fillSheet["Tare Weight(g)"] = 2.2

#OPtion 3 QC Info
newDic = {"INIT": ["Batch#","Stability","Begins","Middle","Ends","Re-Sample","Initials"],
							1: ['111', '100', '5', '500', '5', '500', '5'],
							2: ['121', '200', '5', '1000', '5', '500', '5'],}

##########################SETS NEW Dictionary#############################
CurrentActivityLogger._setQC(newDic)

#OPtion 2 == batchInfo
newDic = {"INIT": ["Batch Code", "Fill Weight", "Total Weight", "Total Wt Range"],
							1: ['111', '100', '5', '500'],
							2: ['121', '200', '5', '1000'],}

##########################SETS NEW Dictionary#############################
CurrentActivityLogger._setBatch(newDic)

#OPtion 1 == PalletInfo
newDic = {'INIT': ['Pallet#', 'Cases', 'Pcs/Case', 'Count', 'Batch#'],
							1: ['111', '100', '5', '500', '1123234'],
							2: ['121', '200', '5', '1000', '1423234'],}

##########################SETS NEW Dictionary#############################
CurrentActivityLogger._setPallet(newDic)

MachineLog = CurrentActivityLogger.getFormatedLog()

CurrentActivityLogger.release()

#START__________________________________________________________________________
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
RunNum = "1"
sql = []
NOW = datetime.datetime.now()

#-------------------------------------------------------------------------------
#--------------------------WORKORDER_RUNS---------------------------------------
#-------------------------------------------------------------------------------

woRunSQLVars = ["WORKORDER_NUM", "RUN_NUM","MACHINE_NUM", "RUN_START", "RUN_END", "FILL_START", "FILL_END",
							"TOTAL_COUNT", "TOTAL_BOXED", "TOTAL_SCRAPPED", "TARE_WEIGHT", "VOLUME", "SPECIFIC_GRAVITY",
							"WEIGHT", "Cosmetic",	"ITEM_NUMBER", "DESIRED_QTY", "FORMULA_REF_NUM","PACKING_CODE", "PACK_OFF",
							"PUMP_NUM", "SIMPLEX_NUM"]

#---------------------------------ZIP---------------------------------------

machineQuery = ["WORKORDER_NUM", "MACHINE_NUM", "RUN_START",
								"RUN_END", "FILL_START", "FILL_END", "TOTAL_COUNT",
								"TOTAL_BOXED", "TOTAL_SCRAPPED"]

machineDictKeys= ["WO","Machine ID", "WO StartTime", "Time Log Created",
									"Fill Start", "Fill End", "TOTAL_COUNT", "Box Count",
									"Fail Count"]

#---------------------------------ZIP2--------------------------------------

fillSheetQuery = ["TARE_WEIGHT", "VOLUME", "SPECIFIC_GRAVITY", "WEIGHT",
									"Cosmetic",	"ITEM_NUMBER", "DESIRED_QTY", "FORMULA_REF_NUM",
									"PACKING_CODE", "PACK_OFF", "PUMP_NUM", "SIMPLEX_NUM"]

fillSheetDictKeys = ["Tare Weight(g)", "Volume(ml)", "    Specific Gravity",
										"Weight(g)", "Cosmetic", "Item Number", "Desired Qty",
										"Formula Ref#", "Packing Code", "Pack Off", "Pump#",
										"Simplex#"]

VarHeaders = ""
EndingString = ""

for MV_DicKey, MV_SQLKey in zip (machineDictKeys,machineQuery):

	if MV_DicKey in MachineLog[0].keys():
		VarHeaders += MV_SQLKey+", "
		if MachineLog[0][MV_DicKey] == None:
			EndingString += "'NULL', "
		else:
			if MV_SQLKey.endswith("_END") or MV_SQLKey.endswith("_START"):

				if MachineLog[0][MV_DicKey] is not None:
					EndingString += "'"+MachineLog[0][MV_DicKey].strftime('%Y-%m-%d %H:%M:%S')+ "', "

				else:
					EndingString += "'"+str(MachineLog[0][MV_DicKey])+"', "

			elif MV_SQLKey == "RUN_NUM":
				EndingString += "'"+str(RunNum)+"', "

			elif MV_SQLKey == "TOTAL_BOXED" or MV_SQLKey == "TOTAL_COUNT":
				EndingString += "'"+str(sum(MachineLog[0][MV_DicKey]))+"', "

			else:
				EndingString += "'"+str(MachineLog[0][MV_DicKey])+"', "

for FS_DicKey, FS_SQLKey in zip(fillSheetDictKeys, fillSheetQuery):
	if FS_DicKey in MachineLog[3].keys():
		VarHeaders += FS_SQLKey+", "
		if MachineLog[3][FS_DicKey] == None:
			EndingString += "'NULL', "
		else:
			EndingString += "'"+str(MachineLog[3][FS_DicKey])+"', "


sql.append("INSERT INTO WORKORDER_RUNS ("+VarHeaders[:-2]+") VALUES ("+EndingString[:-2]+");")

#-------------------------------------------------------------------------------
#--------------------------DOWNTIMES--------------------------------------------
#-------------------------------------------------------------------------------

#1) Maitenance, 2) Inventory, 3) Quality_Control 4) Break 5) ChangeOver
# 'ChangeOver','Maitenance','Inventory','Quality_Control','Break'
# WORKORDER_NUM, RUN_NUM, TYPE, START, END, EMP_BD, EMP_BU
VarHeaders = "WORKORDER_NUM, MACHINE_NUM, RUN_NUM, TYPE, START, END, EMP_BD, EMP_BU"
EndingString = ""

ChangeDwnTime = ("ChangeOver", MachineLog[0]["ChangeOver Time"])
MainDwnTime = ("Maitenance", MachineLog[0]["Maintanance Down Times"])
InvDwnTime = ("Inventory", MachineLog[0]["Inventory Down Time"])
QualDwnTime = ("Quality_Control", MachineLog[0]["Quality Control Down Time"])
BreakDwnTime = ("Break", MachineLog[0]["Break Down Time"])

for reason, DWN_Tmes in [ChangeDwnTime, MainDwnTime, InvDwnTime, QualDwnTime, BreakDwnTime]:

	for DWN_Tme in DWN_Tmes:
		sql.append("INSERT INTO DOWNTIMES ("+VarHeaders+") VALUES ( '%s','%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[0]["WO"],MachineLog[0]["Machine ID"], str(RunNum), reason, DWN_Tme[0][0].strftime('%Y-%m-%d %H:%M:%S'), DWN_Tme[1][0].strftime('%Y-%m-%d %H:%M:%S'), DWN_Tme[0][1], DWN_Tme[1][1]))

#-------------------------------------------------------------------------------
#--------------------------EMPLOYEE_BADGE_SWIPES--------------------------------
#-------------------------------------------------------------------------------

VarHeaders = "EMPLOYEE_BADGE_NUM, EMP_TYPE, MACHINE_NUM, WORKORDER_NUM, RUN_NUM, TIME_IN, TIME_OUT"

for key in MachineLog[1].keys():
	for times in MachineLog[1][key][1]:

		starttime = times[0].strftime('%Y-%m-%d %H:%M:%S')
		endtime = times[1]

		if endtime is not None:
			endtime = endtime.strftime('%Y-%m-%d %H:%M:%S')
		else:
			endtime = NOW.strftime('%Y-%m-%d %H:%M:%S')

		sql.append("INSERT INTO EMPLOYEE_BADGE_SWIPES ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s','%s');" % (key, MachineLog[1][key][0], MachineLog[0]["Machine ID"], MachineLog[0]["WO"], str(RunNum), starttime, endtime))


#-------------------------------------------------------------------------------
#-----------------------------------PALLETS-------------------------------------
#-------------------------------------------------------------------------------
if len(MachineLog[6].keys()) > 1:
	VarHeaders = "PALLET_NUM, BATCH_NUM, WORKORDER_NUM, RUN_NUM, BOXES, PEACES_PER_BOX"

	for key in MachineLog[5].keys():
		print key, type(key), key is not "INIT"
		if key is not "INIT":
			print "IN"
			sql.append("INSERT INTO PALLETS ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s');" % (MachineLog[5][key][0], MachineLog[5][key][4], MachineLog[0]["WO"], str(RunNum), MachineLog[5][key][1], MachineLog[5][key][2]))

#-------------------------------------------------------------------------------
#-----------------------------------BATCHES-------------------------------------
#-------------------------------------------------------------------------------
if len(MachineLog[4].keys()) > 1:
	VarHeaders = "BATCH_NUM, WORKORDER_NUM, MACHINE_NUM, RUN_NUM, FILL_WEIGHT, TOTAL_WEIGHT, TOTAL_WEIGHT_RANGE"

	for key in MachineLog[4].keys():
		print key, type(key), key is not "INIT"
		if key is not "INIT":
			print "In"
			sql.append("INSERT INTO BATCHES ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[4][key][0], MachineLog[0]["WO"], MachineLog[0]["Machine ID"], str(RunNum), MachineLog[4][key][1], MachineLog[4][key][2], MachineLog[4][key][3]))

#-------------------------------------------------------------------------------
#------------------------------------QC-----------------------------------------
#-------------------------------------------------------------------------------
if len(MachineLog[6].keys()) > 1:
	VarHeaders = "MACHINE_NUM, WORKORDER_NUM, RUN_NUM, BATCH_NUM, STABILITY, BEGINS, MIDDLE, ENDS, RESAMPLE, INITIALS"

	for key in MachineLog[6].keys():
		print key, type(key), key is not "INIT"
		if key is not "INIT":
			print "In"
			sql.append("INSERT INTO QC ("+VarHeaders+") VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (MachineLog[0]["Machine ID"], MachineLog[0]["WO"], str(RunNum), MachineLog[6][key][0], MachineLog[6][key][1], MachineLog[6][key][2], MachineLog[6][key][3], MachineLog[6][key][4], MachineLog[6][key][5], MachineLog[6][key][6]))

#-------------------------------------------------------------------------------
#----------------------------------FINALLY--------------------------------------
#-------------------------------------------------------------------------------
"""
# Open database connection
db = MySQLdb.connect("192.168.20.31","cyrus","cyrus2sql","pqmfg_daq")

# prepare a cursor object using cursor() method
cursor = db.cursor()

for SQL_Statment in sql:
	try:
		# Execute the SQL command
		print "SQL: ", SQL_Statment
		cursor.execute(SQL_Statment)
		# Commit your changes in the database
		db.commit()

	except _mysql.Error, e:
		db.rollback()
		print "SQL Error %d: %s" % (e.args[0], e.args[1])

	except:
		# Rollback in case there is any error
		db.rollback()

# disconnect from server
db.close()
"""