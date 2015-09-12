from actuator_names import ActuatorNames
import metaactuators
from collection_wrapper import *

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ntplib
from time import ctime
import csv
import pymongo
from pytz import timezone
import json
import time
import sys, os
from collection_wrapper import CollectionWrapper
from collection import defaultdict
import ntplib
from runtime import Runtime

class Ambulance:
	resetColl = None
	expLogColl = None
	dummyBeginTime = datetime(2000,1,1)
	dummyEndTime = datetime(2030,12,31)
	actuDict = dict()
	timeOffset = None
	ntpURL = 'ntp.ucsd.edu'
	runt = Runtime()
	minResetLatency= 10 # minutes


	def __init__(self):
		self.resetColl = CollectionWrapper('reset_queue')
		self.expLogColl = CollectionWrapper('experience_log')
		self.runt.update_time_offset()



	def emergent_rollback(self):
		queryAll = {}
		resetQueue = self.resetColl.pop_dataframe(queryAll)
		resetQueue = resetQueue.sort(columns='set_time', axis='index')
		if len(resetQueue)==0:
			return None
		resetSeq= defaultdict(list)

		# Make actuators to reset and get earliest set time dependent on reset_queue
		earliestDepTime = self.dummyEndTime
		for row in resetQueue.iterrows():
			uuid = row[1]['uuid']
			name = row[1]['name']
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			actuator = metaactuators.make_actuator(uuid,name,zone,actuType)
			if not uuid in self.actuDict.keys():
				self.actuDict['uuid'] = actuator
			setTime = row[1]['set_time']
			dependentTime = setTime - actuator.get_longest_dependency()
			if earliestDepTime > dependentTime:
				earliestDepTime = dependentTime

		logQuery = {'$and':[{'reset_time':{'$gte':earliestDepTime}},{'reset_time':{'$lte':now}}]}
		expLog = expLogColl.load_dataframe(logQuery)
		
		# Construct reset sequence (dict of list. dict's key is target time)
		#TODO: Filter resetQueue by removing redundant reset signals
		now = self.runt.now()
		while len(resetQueue)>0:
			currResetList = dict()
			for row in resetQueue.iterrows():
				uuid = row[1]['uuid']
				zone = row[1]['zone']
				actuator = self.actuDict[uuid]
				depFlag = False
				for uuid in actuator.get_dependent_actu_list():
					if (uuid in logQuery['uuid'][logQuery['reset_time']>=now-actuator.minLatencty]) or (uuid in currResetList):
						depFlag = True
						break
				if not depFlag:
					currResetList[uuid] = row[1]['reset_value']
					resetQueue = resetQueue.drop(row[2])
			now = now + timedelta(minutes=10)
			resetSeq.append(currResetList)

		# Reset all the sensors registered at reset_queue
		for currResetList in resetSeq:
			for uuid, resetVal in currResetList.iteritems():
				actuator = self.actuDict[uuid]
				now = self.runt.now()
				origVal = actuator.get_latest_value(now)
				expLogRow = ExpLogRow(uuid, actuator.name, now, setVal=actuator.resetVal, origVal=origVal)
				self.expLogColl.store_row(expLogRow)
				actuator.reset_value(resetVal)
			# TODO: I have to acknowledge that the value is reset. However, how can I check if the reset value is -1?? How can I know if the value is reset or just changed?
			time.sleep(self.minResetLatency)

