from building_depot import DataService, BDError
import authdata

from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import numpy as np
from collections import OrderedDict
import operator

#import urllib3
#urllib3.disable_warnings()

# NOTE
# ts=timeseries

#Example of time init
# self.pst.localize(offTime, is_dst=True)

class bdWrapper:

	bdDS = None
	pst = timezone('US/Pacific')
	utc = timezone('UTC')
	bdStrFormat = '%Y-%m-%dT%H:%M:%S+00:00'

	def __init__(self):
		self.bdDS = DataService(authdata.srcUrlBase, authdata.bdApiKey, authdata.bdUserName)

	def get_sensor_uuids(self, context):
# context (a series of dictionary) -> uuid (list)
#context is 
		try:
			resp = self.bdDS.list_sensors(context)
			uuids = list()
			for sensor in resp['sensors']:
				uuids.append(sensor['uuid'])
			return uuids
		except BDError as e:
			print e
			return []


	def get_sensor_ts(self, uuid, sensorType, beginTime, endTime):
# uuid(string), sensorType(string), beginTime(datetime), endTime(datetime) -> timeseries (pd.Series)
# Note: beginTime and endtime should not be normalized already. should be a raw format.
		isoBegin = self.pst.localize(beginTime)
		isoEnd = self.pst.localize(endTime)
		try:
			rawData = self.bdDS.get_timeseries_datapoints(uuid, sensorType, isoBegin, isoEnd)
			pdseries = self.rawts2pdseries(rawData['timeseries'])
			#pdts = self.rawts2pdts(rawData['timeseries'])
			return pdseries
		except BDError as e:
			print e
			return None
		
# TODO: Can I do this better? hard to convert list of dict into dataframe
	def rawts2pdts(self, rawData):
		rawData = OrderedDict([(key,d[key]) for d in rawData for key in d])
		sortedData = rawData
		#rawData = dict([(key,d[key]) for d in rawData for key in d])
		#sortedData = OrderedDict(sorted(rawData.items(), key=operator.itemgetter(0)))
		pdts = pd.DataFrame({'timestamp':sortedData.keys(), 'value':sortedData.values()})
		g = lambda tp:datetime.strptime(tp, self.bdStrFormat).replace(tzinfo=self.utc).astimezone(self.pst)
		pdts['timestamp'] = pdts['timestamp'].apply(g)
		return pdts

	def rawts2pdseries(self,rawData):
		rawData = OrderedDict([(key,d[key]) for d in rawData for key in d])
		for key in rawData.keys():
			newKey = datetime.strptime(key, self.bdStrFormat).replace(tzinfo=self.utc).astimezone(self.pst)
			rawData[newKey] = rawData.pop(key)
		pdseries = pd.Series(data=rawData.values(),index=rawData.keys())
		return pdseries


# TODO: Do not make multiple writing (maybe remove this?)
	def get_zone_sensor_ts(self, zone, template, sensorType, beginTime, endTime):
# zone(string), template(string), sensorType(string), beginTime(datetime), endTime(datetime) -> ts(pd.Series)
# Note: This is a wrapper for easy use of get sensor time series
		context = {'room':'rm-'+zone, 'template':template}
		try:
			uuids = self.get_sensor_uuids(context)
			if len(uuids)>1:
				print "ERROR: More than one sensor are found: " + string(len(uuids)) + ' sensors are found'
				return None
			elif len(uuids)==0:
				print "ERROR: No sensor is found"
				return None
			ts = self.get_sensor_ts(uuids[0], sensorType, beginTime, endTime)
			return ts
		except BDError as e:
			print e
			#TODO or just return None?
			return pd.Series()

	def set_sensor_ts(self, uuid, sensorType, ts):
# uuid(string), sensorType(string), ts(list of dict) -> success(boolean)
# An example of ts: [{datetime(2014,1,1,0,0,0):72}]
		newts = list()
		for onedict in ts:
			newts.append({self.pst.localize(onedict.keys()[0]).isoformat(): onedict.values()[0]})

		try:
			self.bdDS.put_timeseries_datapoints(uuid, sensorType, newts)
			return True
		except BDError as e:
			print e
			return False

	def set_sensor_latest(self, uuid, sensorType, value):
		currTime = datetime.now()
		ts = [{currTime:value}]
		return self.set_sensor_ts(uuid,sensorType,ts)

