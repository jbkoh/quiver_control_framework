from bd_wrapper import BDWrapper
from collection_wrapper import CollectionWrapper
from actuator_names import ActuatorNames
from sensor_names import SensorNames
from feature_extractor import FeatureExtractor
from clusterer import Clusterer

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
#import sklearn.cluster.KMeans as KMeans
import pickle
import csv
import json
from quiver import QRError


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
		self.zonelist = self.csv2list('metadata/partialzonelist.csv')
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

	def normalize_data(self, rawData, beginTime, endTime):
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

	def receive_a_sensor(self, zone, actuType, beginTime, endTime):
		uuid = self.get_actuator_uuid(zone, actuType)
		rawData = self.bdm.get_sensor_ts(uuid, 'PresentValue', beginTime, endTime)
		procData = self.normalize_data(rawData, beginTime, endTime)
		return procData
	
	def receive_entire_sensors(self, beginTime, endTime):
		#TODO: Should be parallelized here
		filename='data/'+beginTime.isoformat()[0:-7].replace(':','_') + '.pkl'
		dataDict = dict()
		for zone in self.zonelist:
			zoneDict = dict()
			for actuType in self.actuNames.nameList+self.sensorNames.nameList:
				try:
					uuid = self.get_actuator_uuid(zone, actuType)
				except QRError:
					continue
				data = self.receive_a_sensor(zone, actuType, beginTime, endTime)
				zoneDict[actuType] = data
			dataDict[zone] = zoneDict

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



