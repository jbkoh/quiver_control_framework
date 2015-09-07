from actuator_names import ActuatorNames
import metaactuators
from collection_wrapper import CollectionWrapper

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

import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 62122))

class Ambulance:
	resetColl = None
	expLogColl = None
	dummyBeginTime = datetime(2000,1,1)
	dummyEndTime = datetime(2030,12,31)
	actuDict = dict()
	timeOffset = None
	ntpURL = 'ntp.ucsd.edu'
	runt = Runtime()


	def __init__(self):
		self.resetColl = CollectionWrapper('reset_queue')
		self.expLogColl = CollectionWrapper('experience_log')
		self.runt.update_time_offset()



	def emergent_rollback(self):
#		queryAll = {'reset_time':{'$gte':self.dummyBeginTime}}
		queryAll = {}
		resetQueue = self.resetColl.pop_data(queryAll)
		resetQueue = resetQueue.sort(columns='set_time', axis='index')
		if len(resetQueue)==0:
			return None
		resetSequence = defaultdict(list)

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
		for row in resetQueue.iterrows():
			uuid = row[1]['uuid']
			actautor = self.actuDict[uuid]
			setTime = self.runt.now()
			for 
			#TODO: check dependency and put the reset sequence to 
