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

from multiprocessing import Process


class Runtime:
	ntpURL = 'ntp.ucsd.edu'
	timeOffset = timedelta(0)
	ntpClient = None
	inputTimeFormat = '%m/%d/%Y %H:%M:%S'
	actuDict= dict()
	actuNames = ActuatorNames()
	commandColl = None

	def __init__(self):
		self.ntpClient = ntplib.NTPClient()
		client = pymongo.MongoClient()
		db = client.quiverdb
		self.commandColl = CollectionWrapper('command_sequence')
		pass

	def update_offset(self):
		ntpRequest = self.ntpClient.request(self.ntpURL)
		ntpRequest.tx_time
		ntpTime = datetime.strptime(time.ctime(ntpRequest.tx_time), "%a %b %d %H:%M:%S %Y")
		self.timeOffset = ntpTime - datetime.now()

	def issue_command(self, command):
		pass
	
	def read_seq(self, filename):
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
	
	def store_seq(self, command):
		self.commandColl.store_dataframe(command)

	def load_seq(self, beginTime, endTime):
		query = {'$and':[{'timestamp':{'$lte':endTime}}, {'timestamp':{'$gte':beginTime}}]}
		return self.commandColl.load_dataframe(query)

	def actuator_exist(self, zone, actuatorType):
# zone(string), actuatortype(string) -> existing?(boolean)
		if [zone, actuatorType] in self.actuDict.keys():
			return True
		else:
			return False

	def validate_command_seq_freq(self,seq):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			actuator  = self.actuDict[[zone, actuType]]
			minLatency = actuator.minLatency
			tp = row[1]['timestamp']
			inrangeRows = np.bitwise_and(seq['timestamp']<tp+minLatency, seq['timestamp']>tp-minLatency)
			inrangeRows = seq.iloc[inrangeRows]
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
			actuator  = self.actuDict[[zone, actuType]]
			minLatency = actuator.minLatency
			tp = row[1]['timestamp']
			inrangeRowaIdx = np.bitwise_and(seq['timestamp']<tp, seq['timestamp']>=tp-minExpLatency)
			inrangeRows = seq.iloc[inrangeRowsIdx]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and actuator.check_dependency(inrangeRow[1]['actuator_type']):
					print baseInvalidMsg + str(row[1]) + ' is dependent on ' + str(inrangeRow[1])
					return False
		return True

	def validate_command_seq(self, seq):
		self.validate_command_seq_freq(self,seq)
		self.validate_command_seq_dependency(self,seq)

	def top_ux(self):
		pass

	def top_dynamic_control(self):
		while(True):
			self.update_offset()
		

	def top(self):
		uxProc = Process(target=self.top_ux, args=args1)
		dynamicControlProc = process(target=self.top_dynamic_control, args=args2)
		uxProc.start()
		dynamicControlProc.start()
		uxProc.join()
		dynamicControlProc.join()
