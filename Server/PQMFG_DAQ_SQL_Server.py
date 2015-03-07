#!/usr/bin/python

import MySQLdb
import time

# Open database connection
db = MySQLdb.connect("192.168.20.31","cyrus","cyrus2sql","pqmfg_daq")

# prepare a cursor object using cursor() method
cursor = db.cursor()

# Drop table if it already exist using execute() method.
cursor.execute("DROP TABLE IF EXISTS QC")

# Create table as per requirement
sql = """CREATE TABLE QC (
	MACHINE_NUM INT NOT NULL,
	WORKORDER_NUM INT NOT NULL,
	RUN_NUM INT NOT NULL,
	BATCH_NUM varchar(255),
	STABILITY varchar(255),
	BEGINS varchar(255),
	MIDDLE varchar(255),
	ENDS varchar(255),
	RESAMPLE varchar(255),
	INITIALS varchar(255))"""

cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS DOWNTIMES")

# Create table as per requirement
sql = """CREATE TABLE DOWNTIMES (
	MACHINE_NUM INT NOT NULL,
	WORKORDER_NUM INT NOT NULL,
	RUN_NUM INT NOT NULL,
	TYPE ENUM('ChangeOver','Maitenance','Inventory','Quality_Control','Break') NOT NULL,
	START DateTime,
	END DateTime,
	EMP_BD int,
	EMP_BU int)"""

cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS BATCHES")

sql = """CREATE TABLE BATCHES (
	BATCH_NUM varchar(255) NOT NULL,
	WORKORDER_NUM INT NOT NULL,
	MACHINE_NUM INT NOT NULL,
	RUN_NUM INT NOT NULL,
	FILL_WEIGHT Float,
	TOTAL_WEIGHT Float,
	TOTAL_WEIGHT_RANGE varchar(255))"""

cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS EMPLOYEE_BADGE_SWIPES")

sql = """CREATE TABLE EMPLOYEE_BADGE_SWIPES (
	EMPLOYEE_BADGE_NUM varchar(255) NOT NULL,
	EMP_TYPE ENUM('Line_Worker','Line_Leader','Mechanic'),
	WORKORDER_NUM INT NOT NULL,
	RUN_NUM INT NOT NULL,
	MACHINE_NUM INT NOT NULL,
	TIME_IN DATETIME NOT NULL,
	TIME_OUT DATETIME NOT NULL)"""

cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS WORKORDER_RUNS")

sql = """CREATE TABLE WORKORDER_RUNS (
	WORKORDER_NUM INT NOT NULL,
	RUN_NUM INT NOT NULL,
	MACHINE_NUM INT NOT NULL,
	RUN_START DateTime,
	RUN_END DateTime,
	FILL_START DateTime,
	FILL_END DateTime,
	TOTAL_COUNT INT,
	TOTAL_BOXED INT,
	TOTAL_SCRAPPED INT,
	TARE_WEIGHT Float,
	VOLUME Float,
	SPECIFIC_GRAVITY Float,
	WEIGHT Float,
	Cosmetic Float,
	ITEM_NUMBER varchar(255),
	DESIRED_QTY INT,
	FORMULA_REF_NUM varchar(255),
	PACKING_CODE varchar(255),
	PACK_OFF boolean,
	PUMP_NUM int,
	SIMPLEX_NUM int)"""

cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS PALLETS")

sql = """CREATE TABLE PALLETS (
	PALLET_NUM INT NOT NULL,
	BATCH_NUM varchar(255) NOT NULL,
	WORKORDER_NUM INT NOT NULL,
	RUN_NUM INT NOT NULL,
	BOXES INT,
	PEACES_PER_BOX INT)"""

cursor.execute(sql)


# disconnect from server
db.close()

