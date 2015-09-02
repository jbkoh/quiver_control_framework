from actuator_names import ActuatorNames
import metaactuators
import collection_wrapper
reload(collection_wrapper)
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

#from multiprocessing import Process
import threading

# NOTE:
# 1. Information is only shared through DB Collections. Each collection has lock for synchronization.

class Runtime:
	ntpURL = 'ntp.ucsd.edu'
	timeOffset = timedelta(0)
	ntpClient = None
	inputTimeFormat = '%m/%d/%Y %H:%M:%S'
	actuDict= dict()
	actuNames = ActuatorNames()
	futureCommColl = None 	# This is a collection for future command sequence. If some of the commands are issues, they are removed from here.
	logColl = None	 		# This is a collection for log of control. If a command is issued, it is added to here with relevant information.

	def __init__(self):
		futureCommLock = threading.Lock()
		self.ntpClient = ntplib.NTPClient()
		client = pymongo.MongoClient()
		db = client.quiverdb
		self.futureCommColl = CollectionWrapper('command_sequence', futureCommLock)
		pass

	def update_offset(self):
		ntpRequest = self.ntpClient.request(self.ntpURL)
		ntpRequest.tx_time
		ntpTime = datetime.strptime(time.ctime(ntpRequest.tx_time), "%a %b %d %H:%M:%S %Y")
		self.timeOffset = ntpTime - datetime.now()
		return self.timeOffset

	def issue_command(self, command):
		pass
	
	def read_seqfile(self, filename):
# filename(string, excel) -> seqList(pd.DataFrame)
		seqList = pd.read_excel(filename)
		for row in seqList.iterrows():
			zone = row[1]['zone']
			actuatorType = row[1]['actuator_type']
			if not self.actuator_exist(zone, actuatorType):
				oneActu = metaactuators.make_actuator(zone,actuatorType)
				if oneActu:
					self.actuDict[(zone, actuatorType)] = oneActu
		seqList['timestamp'] = pd.to_datetime(seqList['timestamp'])
		return seqList
	
	def store_futureseq(self, command):
		self.futureCommColl.store_dataframe(command)

	def load_future_seq(self, beginTime, endTime):
		query = {'$and':[{'timestamp':{'$lte':endTime}}, {'timestamp':{'$gte':beginTime}}]}
		futureSeq = self.futureCommColl.load_dataframe(query)
		return futureSeq

	def actuator_exist(self, zone, actuatorType):
# zone(string), actuatortype(string) -> existing?(boolean)
		if [zone, actuatorType] in self.actuDict.keys():
			return True
		else:
			return False
			
	def rollback_to_genie_setting(self):
		pass

	def validate_command_seq_freq(self,seq):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			actuator  = self.actuDict[(zone, actuType)]
			minLatency = actuator.minLatency
			tp = row[1]['timestamp']
			inrangeRows = np.bitwise_and(seq['timestamp']<tp+minLatency, seq['timestamp']>tp-minLatency)
			inrangeRows = seq.iloc[inrangeRows.values.tolist()]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and inrangeRow[1]['actuator_type']==actuType:
					print baseInvalidMsg + str(row[1]) + ' is overlapped with ' + str(inrangeRow[1])
					return False
		return True
	
	def validate_command_seq_dependency(self, seq, minExpLatency):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			actuator  = self.actuDict[(zone, actuType)]
			minLatency = actuator.minLatency
			tp = row[1]['timestamp']
			inrangeRowsIdx = np.bitwise_and(seq['timestamp']<tp, seq['timestamp']>=tp-minExpLatency)
			inrangeRows = seq.iloc[inrangeRowsIdx.values.tolist()]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and actuator.check_dependency(inrangeRow[1]['actuator_type']):
					print baseInvalidMsg + str(row[1]) + ' is dependent on ' + str(inrangeRow[1])
					return False
		return True

	def validate_command_seq(self, seq):
		return self.validate_command_seq_freq(seq) and \
				self.validate_command_seq_dependency(seq, timedelta(minutes=5))

	def top_ux(self):
		seqFileType = 'xlsx'
		while(1):
			shellCommand = raw_input("Command: ")
			if seqFileType in shellCommand:
		#	if False:
				# Receive a new sequence filename
				newFilename = shellCommand
				newSeq = self.read_seqfile(newFilename)
				if self.validate_command_seq(newSeq):
					self.store_futureseq(newSeq)
					print "Input commands are successfully stored"
				else:
					print "Input commands are not valld"
			print 'UX'
			time.sleep(1)

	def now(self):
		currTime = datetime.now()
		currTime + self.timeOffset
		return currTime

	def issue_seq(self, seq):
		# TODO: Implement this!
		pass

	def top_dynamic_control(self):
		dummyBeginTime = datetime(2000,1,1)
		controlInterval = 5 # in seconds
		while(True):
			#print "begin controlled"
			currTime = self.now()
			futureCommands = self.load_future_seq(dummyBeginTime, currTime+timedelta(controlInterval))
			self.issue_seq(futureCommands)
			#TODO From here
			time.sleep(controlInterval)

	def top_ntp(self):
		while(True):
			print self.update_offset()
			time.sleep(15*60) # synchronized to NTP server in every 15 minutes

	def top(self):
		print '=============Begin of Quiver============='
		controlT = threading.Thread(target=self.top_dynamic_control)
		controlT.daemon = True
		uxT = threading.Thread(target=self.top_ux)
		uxT.daemon = True
		ntpT = threading.Thread(target=self.top_ntp)
		ntpT.daemon = True
		controlT.start()
		uxT.start()
		ntpT.start()
		while(1):
			pass
#		uxT.join()
#		controlT.join()
#		ntpT.join()
		self.rollback_to_genie_setting()
		print '==============End of Quiver=============='
