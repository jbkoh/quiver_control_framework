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
from math import sqrt
from sklearn.metrics import mean_squared_error




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
		#filename = 'data/controldata_nextval.pkl'
		#filename = 'data/4132_2014.pkl'
		filename = 'data/3152_09302015.pkl'
		filenameList.append(filename)
		filename = 'data/3109_09302015.pkl'
		filenameList.append(filename)
		filename = 'data/2150_09132015.pkl'
		filenameList.append(filename)
		filename = 'data/2148_01012015.pkl'
		filenameList.append(filename)
		fig = plt.figure()
		ax = fig.add_subplot(111,projection='3d')

		testFilenameList = list()
		testFilenameList.append('data/2150_01012015.pkl')
		testFilenameList.append('data/4148_09012015.pkl')
		testFilenameList.append('data/2112_09012015.pkl')

		dataList = list()
#		for idx, filename in enumerate(filenameList):
#			with open(filename, 'rb') as fp:
#				data = pickle.load(fp)
#			if idx==0:
#				dataList.append(self.arrange_data(data['RM-4132']))
#			else:
#				dataList.append(self.arrange_data(data['RM-2108']))

		#for zone in self.testlist:
		#	dataList.append(self.arrange_data(rawDataDict[zone]))
		for idx, filename in enumerate(filenameList):
			with open(filename,'rb') as fp:
				rawDataDict = pickle.load(fp)
				dataList.append(self.arrange_data(rawDataDict))
		
		testDataList = list()
		for idx, filename in enumerate(testFilenameList):
			with open(filename,'rb') as fp:
				rawDataDict = pickle.load(fp)
				testDataList.append(self.arrange_data(rawDataDict))

		if len(testDataList)==1:
			testDataDict = testDataList[0]
		else:
			testDataDict=  self.merge_data(testDataList[0], testDataList[:-1])

#		dataList.append(self.arrange_data(rawDataDict))

		if len(dataList)==1:
			dataDict = dataList[0]
		else:
			dataDict = self.merge_data(dataList[0], dataList[:-1])

		for key, data in dataDict.iteritems():
			print key
			self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1))
	
	def fit_data(self, y, xs, testy, testxs):
		#svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
		svr_rbf = SVR(kernel='rbf')
		#svr_rbf = SVR()
		fitted = svr_rbf.fit(xs,y)
		y_rbf = fitted.predict(xs)
		fig = plt.figure()
		#ax1 = fig.add_subplot(2,2,1,projection='3d')
		#ax1.scatter(xs[xs.keys()[0]],xs[xs.keys()[1]],y,c='k')
		
		#ax2 = fig.add_subplot(2,2,2,projection='3d')
		#ax2.scatter(xs[xs.keys()[0]],xs[xs.keys()[1]],y_rbf,c='k')

		testy_rbf = fitted.predict(testxs)
		#ax3 = fig.add_subplot(2,2,3,projection='3d')
		#ax3.scatter(testxs[testxs.keys()[0]],testxs[testxs.keys()[1]],testy,c='k')

		#ax4 = fig.add_subplot(2,2,4,projection='3d')
		#ax4.scatter(testxs[testxs.keys()[0]],testxs[testxs.keys()[1]],testy_rbf,c='k')
		rmse = sqrt(mean_squared_error(testy, testy_rbf))
		normRmse = rmse/np.mean(testy)

		ax1 = fig.add_subplot(121)
		plotList = list()
		plotList.append(ax1.plot(y, c='b', label='original'))
		plotList.append(ax1.plot(y_rbf, c='r', label='fitted'))
		ax1.set_title('Learning Data')
		ax1.legend()
		plotList = list()
		ax2 = fig.add_subplot(122)
		plotList.append(ax2.plot(testy, c='b', label='original'))
		plotList.append(ax2.plot(testy_rbf, c='r', label='fitted'))
		ax2.set_title('Test Data')
		ax2.legend()

		
		print rmse, normRmse
		print '\n'

		plt.show()

		
		pass
