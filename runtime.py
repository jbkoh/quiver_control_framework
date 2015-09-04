from actuator_names import ActuatorNames
import metaactuators
from collection_wrapper import CollectionWrapper
from bd_wrapper import BDWrapper

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
import smtplib
import logging
import emailauth

#from multiprocessing import Process
#import threading

# NOTE:
# 1. Information is only shared through DB Collections. Each collection has lock for synchronization.

#QRError = Quiber Runtime Error
class QRError(BaseException):
	errorType = None
	value = None
	def __init__(self, errorType=None, value=None):
		self.errorType = errorType
		self.value = value

	def __str__(self):
		return self.errorType + ': ' + repr(self.value)


class Runtime:
	ntpURL = 'ntp.ucsd.edu'
	timeOffset = timedelta(0)
	ntpClient = None
	inputTimeFormat = '%m/%d/%Y %H:%M:%S'
	actuDict= dict()
	actuNames = ActuatorNames()
	futureCommColl = None 	# This is a collection for future command sequence. If some of the commands are issued, they are removed from here.
	expLogColl = None	 		# This is a collection for log of control. If a command is issued, it is added to here with relevant information.
	resetColl = None		# This is a collection for rollback. If a command is issued, its corresponding rollback command is added here.
	relinquishVal = -1
	ambulanceConn = None
	ntpActivateTime = None
	dummyBeginTime = datetime(2000,1,1)
	dummyEndTime = datetime(2030,12,31,0,0,0)
	bdm = None

	def __init__(self):
#		futureCommLock = threading.Lock()
		self.ntpClient = ntplib.NTPClient()
		client = pymongo.MongoClient()
		self.futureCommColl = CollectionWrapper('command_sequence')
		self.resetColl = CollectionWrapper('reset_queue')
		self.expLogColl = CollectionWrapper('experience_log')
		self.ntpActivateTime = self.dummyBeginTime
		logging.basicConfig(filname='log/debug.log',level=logging.DEBUG)
		self.bdm = BDWrapper()
				
	def notify_systemfault(self):
		msg = "Quiver control system bas been down at " + self.now().isoformat()
		self.notify_email(msg)

	def notify_email(self, msg):
		server = smtplib.SMTP(emailauth.smtpURL)
		server.starttls()
		server.login(emailauth.username, emailauth.password)
		server.sendmail(emailauth.fromaddr, emailauth.toaddrs, msg)
		server.quit()

	def update_time_offset(self):
		ntpRequest = self.ntpClient.request(self.ntpURL)
		ntpRequest.tx_time
		ntpTime = datetime.strptime(time.ctime(ntpRequest.tx_time), "%a %b %d %H:%M:%S %Y")
		self.timeOffset = ntpTime - datetime.now()
		return ntpTime
	
	def get_actuator_uuid(self, zone=None, actuType=None):
		context = dict()
		if zone != None:
			context['room']=zone
		if actuType != None:
			context['template']=actuType
		uuids = self.bdm.get_sensor_uuids(context)
		if len(uuids)>1:
			raise QRError('Many uuids are found', context)
		elif len(uuids)==0:
			raise QRError('No uuid is found', context)
		else:
			return uuids[0]
	
	def get_actuator_name(self,zone=None,actuType=None):
		context = dict()
		if zone != None:
			context['room']=zone
		if actuType != None:
			context['template']=actuType
		uuids = self.bdm.get_sensor_names(context)
		if len(uuids)>1:
			raise QRError('Many uuids are found', context)
		elif len(uuids)==0:
			raise QRError('No uuid is found', context)
		else:
			return uuids[0]

	def read_seqfile(self, filename):
# filename(string, excel) -> seqList(pd.DataFrame)
		seqList = pd.read_excel(filename)
		for row in seqList.iterrows():
			zone = row[1]['zone']
			actuatorType = row[1]['actuator_type']
			uuid = self.get_actuator_uuid(zone,actuatorType)
			name = self.get_actuator_name(zone,actuatorType)
			seqList['name'][row[0]] = name
			seqList['uuid'][row[0]] = uuid
			value = row[1]['value']
			if not self.actuator_exist(uuid):
				oneActu = metaactuators.make_actuator(uuid, name, zone=zone,actuType=actuatorType)
				if oneActu:
					self.actuDict[uuid] = oneActu
				else:
					raise QRError('Failed to make an actuator', [uuid, anme])
			actuator = self.actuDict[uuid]
			if not actuator.validate_input(value):
				raise QRError('Invald input', [uuid, name, value])
		seqList['set_time'] = pd.to_datetime(seqList['set_time'])
		seqList['reset_time'] = pd.to_datetime(seqList['reset_time'])
		return seqList
	
	# command(pd.DataFrame) -> X
	def store_future_seq(self, seq):
		self.futureCommColl.store_dataframe(seq)

	def load_future_seq(self, beginTime, endTime):
		query = {'$and':[{'set_time':{'$lte':endTime}}, {'set_time':{'$gte':beginTime}}]}
		futureSeq = self.futureCommColl.load_dataframe(query)
		invalidCommand = self.validate_command_seq(futureSeq)
		if invalidCommand == None:
			self.futureCommColl.remove_dataframe(query)
			return futureSeq
		else:
			raise QRError(errorType='Invalid command: ', value=invalidCommand)

	def load_reset_seq(self, endTime):
		query = {'reset_time':{'$lte':endTime}}
		futureSeq = self.resetColl.pop_dataframe(query)
		return futureSeq

	def actuator_exist(self, uuid):
# zone(string), actuatortype(string) -> existing?(boolean)
		if uuid in self.actuDict.keys():
			return True
		else:
			return False
			
	def rollback_to_original_setting(self):
		resetSeq = self.load_reset_seq(self.dummyEndTime)
		for row in resetSeq.iterrows():
			currTime = self.now()
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			resetVal = row[1]['reset_value']
			uuid = row[1]['uuid']
			actuator = self.actuDict[uuid]
			actuator.reset_value(resetVal, currTime)
		self.futureCommColl.remove_all()
		self.resetColl.remove_all()

	def validate_command_seq_freq(self,seq):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			actuator  = self.actuDict[uuid]
			minLatency = actuator.minLatency
			tp = row[1]['set_time']
			inrangeRows = np.bitwise_and(seq['set_time']<tp+minLatency, seq['set_time']>tp-minLatency)
			inrangeRows = np.bitwise_and(inrangeRows, seq['zone']==zone)
			inrangeRows = np.bitwise_and(inrangeRows, seq['actuator_type']==actuType)
			inrangeRows[row[0]] = False
			inrangeRows = seq.iloc[inrangeRows.values.tolist()]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and inrangeRow[1]['actuator_type']==actuType:
					print baseInvalidMsg + str(row[1]) + ' is overlapped with ' + str(inrangeRow[1])
					return row[1]
		return None
	
	def validate_command_seq_dependency(self, seq, minExpLatency):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			actuator  = self.actuDict[uuid]
			minLatency = actuator.minLatency
			tp = row[1]['set_time']
			inrangeRowsIdx = np.bitwise_and(seq['set_time']<tp, seq['set_time']>=tp-minExpLatency)
			inrangeRows = seq.iloc[inrangeRowsIdx.values.tolist()]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and actuator.check_dependency(inrangeRow[1]['actuator_type']):
					print baseInvalidMsg + str(row[1]) + ' is dependent on ' + str(inrangeRow[1])
					return row[1]
		return None

	def validate_command_seq(self, seq):
		invalidFreqCommand = self.validate_command_seq_freq(seq)
		if invalidFreqCommand != None:
			return invalidFreqCommand
		invalidDepCommand = self.validate_command_seq_dependency(seq, timedelta(minutes=5))
		if invalidDepCommand != None:
			return invalidDepCommand
		return None

#	def top_ux(self):
#		seqFileType = 'xlsx'
#		while(1):
#			shellCommand = raw_input("Command: ")
#			if seqFileType in shellCommand:
#		#	if False:
#				# Receive a new sequence filename
#				newFilename = shellCommand
#				newSeq = self.read_seqfile(newFilename)
#				if self.validate_command_seq(newSeq):
#					self.store_future_seq(newSeq)
#					print "Input commands are successfully stored"
#				else:
#					print "Input commands are not valld"
#			print 'UX'
#			time.sleep(1)

	def now(self):
		currTime = datetime.now()
		currTime = currTime + self.timeOffset
		return currTime

#TODO: Think about how to handle errors
	def issue_seq(self, seq):
		for row in seq.iterrows():
			tp = row[1]['set_time']
			zone = row[1]['zone']
			setVal = row[1]['value']
			resetTime = row[1]['reset_time']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			name = row[1]['name']
			actuator = self.actuDict[uuid]
			now = self.now()
			origVal = actuator.get_value(now-timedelta(hours=1), now).tail(1)
			print origVal
			if actuType==self.actuNames.commonSetpoint or actuType==self.actuNames.occupiedCommand:
				if actuator.check_control_flag():
					query = {'$and':[{'set_time':{'$lte':now}}, {'zone':zone},{'actuator_type':actuType}]}
					resetVal = self.expLogColl.load_dataframe(query).tail(1)
					resetVal = resetVal['reset_value']
					print resetVal
				else:
					resetVal = origVal
			else:
				resetVal = self.relinquishVal
			print "resetVal: ", resetVal

			actuator.set_value(setVal, tp) #TODO: This should not work in test stage
			resetDF = pd.DataFrame(data={'name':name, 'uuid':uuid, 'reset_time':resetTime,'zone':zone,'actuator_type':actuType, 'reset_value':resetVal, 'actuator_type':actuType}, index=[0])
			self.resetColl.store_dataframe(resetDF)
			expLogDF = pd.DataFrame(data={'name':name, 'uuid':uuid, 'set_time':self.now(), 'reset_time':resetTime, 'zone':zone, 'actuator_type':actuType, 'set_value':setVal, 'reset_value':resetVal, 'original_value':origVal},index=[0])
			self.expLogColl.store_dataframe(expLogDF)

		# wait for ack from BD (TODO: is it correct to wait for BD to response?)
		#TODO: Implement this

			
	def reset_seq(self, seq):
		for row in seq.iterrows():
			print row
			resetTime = row[1]['reset_time']
			zone = row[1]['zone']
			resetVal = row[1]['reset_value']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			actuator = self.actuDict[uuid]
			actuator.reset_value(resetVal, resetTime)

	def top_dynamic_control(self):
		controlInterval = 5 # in seconds
		while(True):
			self.top_ntp()
			currTime = self.now()
			print currTime
			futureCommands = self.load_future_seq(self.dummyBeginTime, currTime+timedelta(seconds=controlInterval))
			print futureCommands
			self.issue_seq(futureCommands)
			resetCommands = self.load_reset_seq(currTime)
			print resetCommands
			self.reset_seq(resetCommands)
			time.sleep(controlInterval)

	def top_ntp(self):
		ntpLatency = timedelta(minutes=30)
		if self.ntpActivateTime<=self.now():
			self.update_time_offset
			self.ntpActivateTime += ntpLatency

	def top_ux(self,filename):
		newSeq = self.read_seqfile(filename)
		invalidCommand = self.validate_command_seq(newSeq)
		if invalidCommand == None:
			self.store_future_seq(newSeq)
			print "Input commands are successfully stored"
			return True
		else:
			raise QRError('Invalid command', invalidCommand)

	def top(self, filename):
		print '=============Begin of Quiver============='
		self.update_time_offset()
		try:
			if self.top_ux(filename):
				self.top_dynamic_control()
			else:
				return None
		except QRError as e:
			print e
			self.notify_systemfault()
			print '==============End of Quiver=============='
		except KeyboardInterrupt:
			if self.resetColl.get_size()!=0:
				self.notify_systemfault()
			print '==============End of Quiver=============='
