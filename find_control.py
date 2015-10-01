import basic
from actuator_names import ActuatorNames
from sensor_names import SensorNames
from bd_wrapper import BDWrapper
from analyzer import Analyzer

import pickle
import pandas as pd
import plotter
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta




class FindControl:
	zonelist = None
	testlist = None
	actuNames = None
	sensorNames = None
	bdm = None
	anal = None

	def __init__ (self):
		self.zonelist = basic.csv2list('metadata/partialzonelist.csv')
		self.testlist = ['RM-4132', 'RM-2150', 'RM-2108']
		self.actuNames = ActuatorNames()
		self.sensorNames = SensorNames()
		self.bdm = BDWrapper()
		self.anal = Analyzer()
	
	def make_dataframe(self, filename):
		data = dict()
		with open(filename, 'rb') as fp:
			dataDict = pickle.load(fp)
			for zone in self.testlist:
				data[zone] = pd.DataFrame.from_dict(dataDict[zone])
		return data

	def make_most_influence_dict(self, df):
		sensorList = np.array(df.keys())
		corrMat = df.corr()

		for sensor in sensorList:
			corrMat[sensor][sensor] = 0
		corrMat = abs(corrMat)

		for sensor in sensorList:
			print sensor

			maxIndices = np.where(corrMat[sensor]>0.5)[0] #This threashold should be defined later
			print corrMat
			if len(maxIndices)==0:
				continue
#			plotData = df[sensorList[maxIndices]]
			plotData = list()
			plotLabel = list()
			for idx in maxIndices:
				plotData.append(df[sensorList[idx]])
				plotLabel.append(sensorList[idx])

			plotter.plot_multiple_2dline(range(0,len(df[sensorList[maxIndices[0]]])), plotData, dataLabels=plotLabel)

# Input: data1(series), data2(series), Output: arranged data2 (list)
	def data_allign(self, data1, data2, direction):
		output = list()
		test = list()
		for tp in data1.index:
			if direction=='right':
				newData = data2[data2.index>tp].head(1)
			elif direction=='left':
				newData = data2[data2.index<=tp].tail(1)
			else:
				print "direction value is wrong"
				return None 

			if newData.empty:
				if direction=='right':
					newData = data2[data2.index<=tp].tail(1)
				elif direction=='left':
					newData = data2[data2.index>=tp].head(1)
				#TODO: Won't it make an error? Will there be a datum always?
			print data1[tp], newData
			test.append(newData)
			output.append(float(newData))
		return output


	def download_control_data(self):
		reqList = list()
		reqList.append(('RM-4132', datetime(2015,9,29,12,01), datetime(2015,9,30,2,59)))
		reqList.append(('RM-2108', datetime(2015,9,29,12,01), datetime(2015,9,30,2,59)))
		acsDF = pd.DataFrame({'acs':[],'cs':[],'oc':[]})
		for req in reqList:
			zoneDict = dict()
			for sensorType in self.actuNames.nameList+self.sensorNames.nameList:
				uuid = self.bdm.get_sensor_uuids({'room':req[0], 'template':sensorType})[0]
				rawData = self.bdm.get_sensor_ts(uuid, 'PresentValue', req[1], req[2])
				zoneDict[sensorType] = rawData
			
			# Actual Cooling Setpoint Data Allignment
			acsSeries = zoneDict[self.actuNames.actualCoolingSetpoint]
			csSeries = zoneDict[self.actuNames.commonSetpoint]
			ocSeries = zoneDict[self.actuNames.occupiedCommand]

			csList = csSeries.tolist()
			acsList = self.data_allign(csSeries, acsSeries, 'right')
			ocList = self.data_allign(csSeries, ocSeries, 'left')
			if not (len(csList)==len(acsList) and len(csList)==len(ocList)):
				print "allignment is wrong"
				return None
			newDF = pd.DataFrame({'acs':acsList, 'cs':csList, 'oc':ocList})
			acsDF = pd.concat([acsDF, newDF])
			
			ocList = ocSeries.tolist()
			csList = self.data_allign(ocSeries, csSeries, 'left')
			acsList = self.data_allign(ocSeries, acsSeries, 'right')
			newDF = pd.DataFrame({'acs':acsList, 'cs':csList, 'oc':ocList})
			acsDF = pd.concat([acsDF, newDF])



	def merge_data(self, data1, dataList):
		dataDict = dict()
		for key in data1.iterkeys():
#			data1[key] = pd.concat([df1, dataList[key]])
			for data in dataList:
				dataDict[key] = pd.concat([data1[key],data[key]])
		return dataDict

	def arrange_data(self, zoneData):
		acsDF = pd.DataFrame({'acs':zoneData[self.actuNames.actualCoolingSetpoint], 'cs':zoneData[self.actuNames.commonSetpoint], 'oc':zoneData[self.actuNames.occupiedCommand]})
		ahsDF = pd.DataFrame({'ahs':zoneData[self.actuNames.actualHeatingSetpoint], 'cs':zoneData[self.actuNames.commonSetpoint], 'oc':zoneData[self.actuNames.occupiedCommand]})
		ccDF = pd.DataFrame({'cc':zoneData[self.actuNames.coolingCommand], 'zt':zoneData[self.sensorNames.zoneTemperature], 'acs':zoneData[self.actuNames.actualCoolingSetpoint]})
		hcDF = pd.DataFrame({'hc':zoneData[self.actuNames.heatingCommand], 'zt':zoneData[self.sensorNames.zoneTemperature], 'ahs':zoneData[self.actuNames.actualHeatingSetpoint]})
		asfspDF = pd.DataFrame({'asfsp':zoneData[self.actuNames.actualSupplyFlowSP], 'cc':zoneData[self.actuNames.coolingCommand], 'hc':zoneData[self.actuNames.heatingCommand], 'ocm':zoneData[self.actuNames.occupiedCoolingMinimumFlow]})
		dcDF = pd.DataFrame({'dc':zoneData[self.actuNames.damperCommand], 'asf':zoneData[self.sensorNames.actualSupplyFlow], 'asfsp':zoneData[self.actuNames.actualSupplyFlowSP]})
		output = dict()
		output['acs'] = acsDF
		output['ahs'] = ahsDF
		output['cc'] = ccDF
		output['hc'] = hcDF
		output['asfsp'] = asfspDF
		output['dc'] = dcDF
		return output

	def organize_data(self):
		#rawDataDict = self.anal.receive_entire_sensors_notstore(datetime(2015,9,29),datetime(2015,9,30,6))
		filenameList = list()
		filename = 'data/controldata_nextval.pkl'
		with open(filename,'rb') as fp:
			rawDataDict = pickle.load(fp)

		dataList = list()
#		for idx, filename in enumerate(filenameList):
#			with open(filename, 'rb') as fp:
#				data = pickle.load(fp)
#			if idx==0:
#				dataList.append(self.arrange_data(data['RM-4132']))
#			else:
#				dataList.append(self.arrange_data(data['RM-2108']))

		for zone in self.testlist:
			dataList.append(self.arrange_data(rawDataDict[zone]))

		dataDict = self.merge_data(dataList[0], dataList[:-1])

		for key, data in dataDict.iteritems():
			print key
			self.fit_data(data[key], data.drop(key,axis=1))
	
	def fit_data(self, y, xs):
		svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
		fitted = svr_rbf.fit(xs,y)
		y_rbf = fitted.predict(xs)
		fig = plt.figure()
		ax1 = fig.add_subplot(1,2,1,projection='3d')
		ax1.scatter(xs[xs.keys()[0]],xs[xs.keys()[0]],y,c='k')
		#plt.show()
		#fig2 = plt.figure()
		ax2 = fig.add_subplot(1,2,2,projection='3d')
		ax2.scatter(xs[xs.keys()[0]],xs[xs.keys()[0]],y_rbf,c='k')
		plt.show()
		pass
