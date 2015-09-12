from actuator_names import ActuatorNames
import metaactuators
from collection_wrapper import *
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
from email.mime.text import MIMEText
import traceback

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
	ackLatency = timedelta(minutes=10)

	def __init__(self):
		self.ntpClient = ntplib.NTPClient()
		client = pymongo.MongoClient()
		self.futureCommColl = CollectionWrapper('command_sequence')
		self.resetColl = CollectionWrapper('reset_queue')
		self.expLogColl = CollectionWrapper('experience_log')
		self.ntpActivateTime = self.dummyBeginTime
		#logging.basicConfig(filname='log/debug.log',level=logging.DEBUG)
		self.bdm = BDWrapper()
				
	def notify_systemfault(self):
		content = "Quiver control system bas been down at " + self.now().isoformat()
		self.notify_email(content)

	def notify_email(self, content):
		server = smtplib.SMTP(emailauth.smtpURL)
		msg = MIMEText('"'+content+'"')
		msg['Subject']='Alert: Quiver is down'
		msg['From'] = emailauth.fromaddr
		msg['To'] = ",".join(emailauth.toaddrs)
		server.starttls()
		server.login(emailauth.username, emailauth.password)
		server.sendmail(emailauth.fromaddr, emailauth.toaddrs, msg.as_string())
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
		decDatetime = lambda x: datetime.strptime(x, self.inputTimeFormat)
		seqList['reset_time'] = seqList['reset_time'].map(decDatetime)
		seqList['set_time'] = seqList['set_time'].map(decDatetime)
		now = self.now()
		if True in (seqList['set_time']<now).tolist():
			raise QRError('some set_time is before now', now)
		for row in seqList.iterrows():
			zone = row[1]['zone']
			actuatorType = row[1]['actuator_type']
			uuid = self.get_actuator_uuid(zone,actuatorType)
			name = self.get_actuator_name(zone,actuatorType)
			seqList['name'][row[0]] = name
			seqList['uuid'][row[0]] = uuid
			value = row[1]['set_value']
			if not self.actuator_exist(uuid):
				oneActu = metaactuators.make_actuator(uuid, name, zone=zone,actuType=actuatorType)
				if oneActu:
					self.actuDict[uuid] = oneActu
				else:
					raise QRError('Failed to make an actuator', [uuid, name])
			actuator = self.actuDict[uuid]
			if not actuator.validate_input(value):
				raise QRError('Invald input', [uuid, name, value])
			resetTime = row[1]['reset_time']
			setTime = row[1]['set_time']
			if resetTime-setTime < actuator.minLatency:
				raise QRError('Latency between set_time and reset_time is too short', [uuid, name, setTime, resetTime])
		#seqList['set_time'] = pd.to_datetime(seqList['set_time'])
		#seqList['reset_time'] = pd.to_datetime(seqList['reset_time'])
		return seqList

	def load_future_seq(self, beginTime, endTime):
		query = {'$and':[{'set_time':{'$lte':endTime}}, {'set_time':{'$gte':beginTime}}]}
		futureSeq = self.futureCommColl.load_dataframe(query)
		invalidCommand = self.dynamic_validate(futureSeq)
		if invalidCommand.empty:
			self.futureCommColl.remove_dataframe(query)
			return futureSeq
		else:
			raise QRError(errorType='A command is depedent to currently opearting actuator', value=invalidCommand)

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
#TODO: This does not consider reset commands. However, it should be considered later
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			actuator  = self.actuDict[uuid]
			minLatency = actuator.minLatency
			setTime = row[1]['set_time']
			inrangeRowsIdx = np.bitwise_and(seq['set_time']<setTime+minLatency, seq['set_time']>setTime-minLatency)
			inrangeRowsIdx = np.bitwise_and(inrangeRowsIdx, seq['uuid']==uuid)
			inrangeRowsIdx[row[0]] = False
			inrangeRows = seq.iloc[inrangeRowsIdx.values.tolist()]
			resetRows = self.resetColl.load_dataframe({'uuid':uuid})
			loggedRows = self.expLogColl.load_dataframe({'$and':[{'set_time':{'$gte':setTime-actuator.minLatency}},{'uuid':uuid}]})
			inrangeRows = pd.concat([inrangeRows, resetRows, loggedRows])
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and inrangeRow[1]['actuator_type']==actuType:
					print baseInvalidMsg + str(row[1]) + ' is overlapped with ' + str(inrangeRow[1])
					return row[1]
		return pd.DataFrame({})
	
	def validate_command_seq_dependency(self, seq, minExpLatency):
# seq(pd.DataFrame) -> valid?(boolean)
		#baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			actuator  = self.actuDict[uuid]
			minLatency = actuator.minLatency
			setTime = row[1]['set_time']
			inrangeRowsIdx = np.bitwise_and(seq['set_time']<setTime, seq['set_time']>setTime-minExpLatency)
			inrangeRows = seq.iloc[inrangeRowsIdx.values.tolist()]
			resetRows = self.resetColl.load_dataframe({})
			loggedRows = self.expLogColl.load_dataframe({'set_time':{'$gte':setTime-minExpLatency}})
			inrangeRows = pd.concat([inrangeRows, resetRows, loggedRows])
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and actuator.get_dependency(inrangeRow[1]['actuator_type'])!=None:
		#			print baseInvalidMsg + str(row[1]) + ' is dependent on ' + str(inrangeRow[1])
					return row[1]
		return pd.DataFrame({})

	def static_validate(self, seq):
		invalidFreqCommand = self.validate_command_seq_freq(seq)
		if not invalidFreqCommand.empty:
			return invalidFreqCommand
		invalidDepCommand = self.validate_command_seq_dependency(seq, timedelta(minutes=5)) #TODO: This minExpLatency should be set to 1 hour later
		if not invalidDepCommand.empty:
			return invalidDepCommand
		return pd.DataFrame({})

	def dynamic_validate(self, seq):
		queryAll = {}
		resetQueue = self.resetColl.load_dataframe(queryAll)
		invalidCommand = pd.DataFrame()
		if resetQueue.empty:
			return pd.DataFrame({})

		for row in seq.iterrows():
			uuid = row[1]['zone']
			actuator = self.actuDict[uuid]
			if True in (resetQueue['uuid'] in actuator.get_dependent_actu_list()).tolist():
				#TODO: Fix this!!!
				return row

		return pd.DataFrame({})

	def now(self):
		currTime = datetime.now()
		currTime = currTime + self.timeOffset
		return currTime

	def issue_seq(self, seq):
		for row in seq.iterrows():
			#logging.debug('Try to issue: ' + repr(seq))
			setTime = row[1]['set_time']
			zone = row[1]['zone']
			setVal = row[1]['set_value']
			resetTime = row[1]['reset_time']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			name = row[1]['name']
			actuator = self.actuDict[uuid]
			now = self.now()
			origVal = actuator.get_value(now-timedelta(hours=1), now).tail(1)[0]
			print origVal
			if actuType in [self.actuNames.commonSetpoint, self.actuNames.occupiedCommand]:
				if actuator.check_control_flag():
					query = {'uuid':uuid}
					resetVal = self.resetColl.load_dataframe(query).tail(1)
					#TODO: This should become more safe. e.g., what if that is no data in resetColl?
					resetVal = float(resetVal['reset_value'])
					print resetVal
				else:
					resetVal = origVal
			else:
				resetVal = self.relinquishVal
			print "resetVal: ", resetVal

			now = self.now()
			actuator.set_value(setVal, setTime) #TODO: This should not work in test stage
			resetRow = ResetRow(uuid, name, setTime=now, resetTime=resetTime, setVal=setVal, resetVal=resetVal, origVal=origVal,actuType=actuType)
			self.resetColl.store_row(resetRow)
			expLogRow = ExpLogRow(uuid, name, setTime=now, resetTime=None, setVal=setVal, resetVal=resetVal, origVal=origVal)
			print expLogRow
			self.expLogColl.store_row(expLogRow)

		# wait for ack from BD (TODO: is it correct to wait for BD to response?)
		if self.issue_ack(seq, True).empty:
			print "Commands are issued"
		else:
			raise QRError('Commands cannot be set at BACNet', seq)

	def issue_ack(self, seq, setResetFlag):
		maxWaitTime = self.now() + timedelta(minutes=11)
		ackInterval = 30 # minutes
		while self.now()<=maxWaitTime:
			for row in seq.iterrows():
				uuid = row[1]['uuid']
				if setResetFlag:
					ackVal = row[1]['set_value']
				else:
					ackVal = row[1]['reset_value']
				actuator = self.actuDict[uuid]
				currT = self.now()
				currVal = actuator.get_latest_value(self.now())
				if currVal==ackVal:
					seq = seq.drop(row[0])
			if len(seq)==0:
				return pd.DataFrame({})
			print "Doing ACK", repr(row[1])
			time.sleep(ackInterval)
		if len(seq)==0:
			return pd.DataFrame({})
		else:
			return seq
			
	def reset_seq(self, seq):
		for row in seq.iterrows():
			#TODO: validate_in_log
			print row
			resetTime = row[1]['reset_time']
			resetVal = row[1]['reset_value']
			actuType = row[1]['actuator_type']
			uuid = row[1]['uuid']
			name = row[1]['name']
			actuator = self.actuDict[uuid]
			now = self.now()
			origVal = actuator.get_value(now-timedelta(hours=1), now).tail(1)[0]
			actuator.reset_value(resetVal, resetTime)
			expLogRow = ExpLogRow(uuid, name, setTime=None, resetTime=resetTime, setVal=None, resetVal=now, origVal=origVal)
			print expLogRow
			self.expLogColl.store_row(expLogRow)

		if not self.issue_ack(seq, False).empty:
			raise QRError('A reset command cannot be set at BACNet', seq)

	def top_dynamic_control(self):
		controlInterval = 5 # in seconds
		while(True):
			self.top_ntp()
			currTime = self.now()
			print currTime
			futureCommands = self.load_future_seq(self.dummyBeginTime, currTime)
			print 'future command:'
			print futureCommands
			self.issue_seq(futureCommands)
			resetCommands = self.load_reset_seq(currTime)
			if len(resetCommands)>0:
				print 'reset command'
				print resetCommands
			self.reset_seq(resetCommands)
			time.sleep(controlInterval)

	def top_ntp(self):
		ntpLatency = timedelta(minutes=30)
		if self.ntpActivateTime<=self.now():
			self.update_time_offset
			self.ntpActivateTime = self.now() + ntpLatency

	def top_ux(self,filename):
		newSeq = self.read_seqfile(filename)
		invalidCommand = self.static_validate(newSeq)
		if invalidCommand.empty:
			self.futureCommColl.store_dataframe(newSeq)
			print "Input commands are successfully stored"
			return True
		else:
			raise QRError('Invalid command', invalidCommand)

	def emergent_rollback(self):
		queryAll = {'reset_time':{'$gte':self.dummyBeginTime}}
		self.resetColl.pop_data(queryAll)

	def system_close_common_behavior(self):
		self.futureCommColl.remove_all()

	def system_refresh(self):
		self.futureCommColl.remove_all()
		self.expLogColl.remove_all()
		self.resetColl.remove_all()

	def top(self, filename):
		self.system_refresh()
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
			self.system_close_common_behavior()
			print '==============End of Quiver=============='
		except KeyboardInterrupt:
			self.system_close_common_behavior()
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print "Error in %s on line %d" % (fname, lineno)
			print "Normally finished by a user interrupt"
			print '==============End of Quiver=============='
#		except Exception, e:
#			print sys.exc_traceback.tb_lineno 
#			print sys.exc_traceback
#			print str(e)
#			print "Unknown error: ", sys.exc_info()[0]
#			if self.resetColl.get_size()!=0:
#				self.notify_systemfault()
#				print 'sent an email'
#			print '==============End of Quiver=============='
