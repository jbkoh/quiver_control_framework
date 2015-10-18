from bd_wrapper import BDWrapper
from collection_wrapper import CollectionWrapper
from actuator_names import ActuatorNames
from sensor_names import SensorNames
from feature_extractor import FeatureExtractor
from clusterer import Clusterer

import pandas as pd
from collections import defaultdict
import numpy as np
from datetime import datetime, timedelta
#import sklearn.cluster.KMeans as KMeans
import pickle
import csv
import json
from quiver import QRError
from copy import deepcopy


class Analyzer:
	bdm = None
	expLogColl = None
	#timeGran = timedelta(minutes=5)
	timeGran = timedelta(minutes=2)
	actuNames = None
	sensorNames = None
	zonelist = None
	feater = None
	clust = None
	
	def __init__(self):
		self.actuNames = ActuatorNames()
		self.sensorNames = SensorNames()
		self.bdm = BDWrapper()
		self.expLogColl = CollectionWrapper('experience_log')
		#self.zonelist = self.csv2list('metadata/partialzonelist.csv')
		self.zonelist = self.csv2list('metadata/zonelist.csv')
		self.feater = FeatureExtractor()
		self.clust = Clusterer()
	
	def csv2list(self, filename):
		outputList = list()
		with open(filename, 'r') as fp:
			reader = csv.reader(fp, delimiter=',')
			for row in reader:
				outputList.append(row[0])
		return outputList

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

	def normalize_data_avg(self, rawData, beginTime, endTime):
		procData = pd.Series({beginTime:float(rawData[0])})
		tp = beginTime
		while tp<=endTime:
			tp = tp+self.timeGran
			leftSeries = rawData[:tp]
			if len(leftSeries)>0:
				idx = len(leftSeries)-1
				leftVal = leftSeries[idx]
				leftIdx = leftSeries.index[idx]
			else:
				leftVal = None
			rightSeries = rawData[tp:]
			if len(rightSeries)>0:
				rightVal = rightSeries[0]
				rightIdx = rightSeries.index[0]
			else:
				rightVal = None
			if rightVal==None and leftVal!=None:
				newVal = leftVal
			elif rightVal!=None and leftVal==None:
				newVal = rightVal
			elif tp==leftIdx:
				newVal = leftVal
			elif tp==rightIdx:
				newVal = rightVal
			elif rightVal!=None and leftVal!=None:
				leftDist = (tp - leftIdx).total_seconds()
				rightDist = (rightIdx - tp).total_seconds()
				newVal = (leftVal*rightDist+rightVal*leftDist)/(rightDist+leftDist)
			else:
				print "ERROR: no data found in raw data"
				newVal = None
			newData = pd.Series({tp:newVal})
			procData = procData.append(newData)
		return procData

	def normalize_data_nextval_deprecated(self, rawData, beginTime, endTime):
		procData = pd.Series({beginTime:float(rawData[0])})
		tp = beginTime
		while tp<=endTime:
			tp = tp+self.timeGran
			leftSeries = rawData[:tp]
			if len(leftSeries)>0:
				idx = len(leftSeries)-1
				leftVal = leftSeries[idx]
				leftIdx = leftSeries.index[idx]
			else:
				leftVal = None
			rightSeries = rawData[tp:]
			if len(rightSeries)>0:
				rightVal = rightSeries[0]
				rightIdx = rightSeries.index[0]
			else:
				rightVal = None

			if rightVal != None:
				newVal = rightVal
			else:
				newVal = leftVal

			newData = pd.Series({tp:newVal})
			procData = procData.append(newData)
		return procData

	def normalize_data(self, rawData, beginTime, endTime, normType):
		rawData = rawData[beginTime:endTime]
		if not beginTime in rawData.index:
			rawData[beginTime] = rawData.head(1)[0]
			rawData = rawData.sort_index()
		if not endTime in rawData.index:
			rawData[endTime] = rawData.tail(1)[0]
			rawData = rawData.sort_index()
		if normType=='nextval':
			procData = rawData.resample('2Min', fill_method='pad')
		elif normType=='avg':
			procData = rawData.resample('2Min', how='mean')
		else:
			procData = None

		return procData
		

	def receive_a_sensor(self, zone, actuType, beginTime, endTime, normType):
		print zone, actuType
		uuid = self.get_actuator_uuid(zone, actuType)
		rawData = self.bdm.get_sensor_ts(uuid, 'PresentValue', beginTime, endTime)
		if actuType!=self.actuNames.damperCommand:
			rawData = self.remove_negativeone(rawData)
		procData = self.normalize_data(rawData, beginTime, endTime, normType)
		return procData

	def receive_entire_sensors_notstore(self, beginTime, endTime, normType, exceptZoneList=[]):
		#TODO: Should be parallelized here
		dataDict = dict()
		for zone in self.zonelist:
			if not zone in exceptZoneList:
				dataDict[zone] = self.receive_zone_sensors(zone, beginTime, endTime, normType)
		return dataDict
	
	def receive_entire_sensors(self, beginTime, endTime, filename, normType, exceptZoneList=[]):
#		filename='data/'+beginTime.isoformat()[0:-7].replace(':','_') + '.pkl'
		dataDict = self.receive_entire_sensors_notstore(beginTime, endTime, normType, exceptZoneList=exceptZoneList)
		with open(filename, 'wb') as fp:
			pickle.dump(dataDict, fp)
#			json.dump(dataDict,fp)

	def clustering(self, inputData, dataDict):
		fftFeat = self.feater.get_fft_features(inputData, dataDict)
		minmaxFeat = self.feater.get_minmax_features(dataDict)
		dtwFeat = self.feater.get_dtw_features(inputData, dataDict)
		freqFeat = self.feater.get_freq_features(inputData, dataDict)
		featDict = dict()
		for zone in self.zonelist:
			featList = list()
			featList.append(fftFeat[zone])
			featList.append(minmaxFeat[zone])
			featList.append(dtwFeat[zone])
			#featList.append(freqFeat[zone])
			featDict[zone] = featList
		print featDict['RM-4132']
		return self.clust.cluster_kmeans(featDict)
	
	def remove_negativeone(self, data):
		if -1 in data.values:
			indices = np.where(data==-1)
			for idx in indices:
				data[idx] = data[idx-1]
		return data

	def receive_zone_sensors(self, zone, beginTime, endTime, normType):
		zoneDict = dict()
		for actuType in self.actuNames.nameList+self.sensorNames.nameList:
			if actuType=='Actual Supply Flow':
				pass
			try:
				uuid = self.get_actuator_uuid(zone, actuType)
			except QRError:
				continue
#			if actuType == self.actuNames.commonSetpoint:
#				wcad = self.receive_a_sensor(zone, 'Warm Cool Adjust', beginTime, endTime, normType)
#				data = self.receive_a_sensor(zone, actuType, beginTime, endTime, normType)
#				data = data + wcad
#				pass
			if actuType != self.actuNames.damperCommand:
				if actuType==self.actuNames.occupiedCommand:
					pass
				data = self.receive_a_sensor(zone, actuType, beginTime, endTime, normType)
			else:
				data = self.receive_a_sensor(zone, actuType, beginTime, endTime, normType)
			zoneDict[actuType] = data
		return zoneDict


	def store_zone_sensors(self, zone, beginTime, endTime, normType, filename):
		data = self.receive_zone_sensors(zone, beginTime, endTime, normType)
		with open(filename, 'wb') as fp:
			pickle.dump(data, fp)

	def store_minmax_dict(self):
		minDict = defaultdict(dict)
		maxDict = defaultdict(dict)
		beginTime = datetime(2015,2,1)
		endTime = datetime(2015,9,1)
		shortBeginTime = datetime(2015,8,1)
		shortEndTime = datetime(2015,8,2)

		for zone in self.zonelist:
			for pointType in self.actuNames.nameList+self.sensorNames.nameList:
				try:
					if pointType=='Occupied Command':
						minDict[zone][pointType] = 1
						maxDict[zone][pointType] = 3
					elif pointType=='Cooling Command':
						minDict[zone][pointType] = 0
						maxDict[zone][pointType] = 100
					elif pointType=='Cooling Command' or pointType=='Heating Command':
						minDict[zone][pointType] = 0
						maxDict[zone][pointType] = 100
					elif pointType=='Occupied Clg Min' or pointType=='Occupied Htg Flow' or pointType=='Cooling Max Flow':
						uuid = self.get_actuator_uuid(zone, pointType)
						data = self.bdm.get_sensor_ts(uuid, 'Presentvalue', shortBeginTime, shortEndTime)
						minDict[zone][pointType] = min(data)
						maxDict[zone][pointType] = max(data)
					elif pointType=='Temp Occ Sts':
						minDict[zone][pointType] = 0
						maxDict[zone][pointType] = 1
					elif pointType=='Reheat Valve Command':
						minDict[zone][pointType] = 0
						maxDict[zone][pointType] = 100
					elif pointType=='Actual Supply Flow' or pointType=='Actual Sup Flow SP':
						uuid = self.get_actuator_uuid(zone, pointType)
						data = self.bdm.get_sensor_ts(uuid, 'Presentvalue', shortBeginTime, shortEndTime)
						maxFlow = data[0]
						minDict[zone][pointType] = 0
						maxDict[zone][pointType] = maxFlow
					elif pointType=='Damper Position':
						minDict[zone][pointType] = 0
						maxDict[zone][pointType] = 100
					elif pointType=='Damper Command':
						uuid = self.get_actuator_uuid(zone, pointType)
						data = self.bdm.get_sensor_ts(uuid, 'Presentvalue', shortBeginTime, shortEndTime)
						meanData = np.mean(data)
						stdData = np.std(data)
						meanAgain = np.mean(data[np.logical_and(data<=meanData+2*stdData, data>=meanData-2*stdData)])
						minDict[zone][pointType] = meanData-2*stdData
						maxDict[zone][pointType] = meanData+2*stdData
					else:
						uuid = self.get_actuator_uuid(zone, pointType)
						data = self.bdm.get_sensor_ts(uuid, 'Presentvalue', beginTime, endTime)
						minDict[zone][pointType] = min(data)
						maxDict[zone][pointType] = max(data)

				except:
					print "Something is wrong"
					pass
		with open('metadata/mindict.pkl', 'wb') as fp:
			pickle.dump(minDict, fp)
		with open('metadata/maxdict.pkl', 'wb') as fp:
			pickle.dump(maxDict, fp)


