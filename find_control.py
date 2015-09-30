import basic
from actuator_names import ActuatorNames
from sensor_names import SensorNames
import pickle

import pandas as pd
import plotter
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from mpl_toolkits.mplot3d import Axes3D




class FindControl:
	zonelist = None
	testlist = None
	actuNames = None
	sensorNames = None

	def __init__ (self):
		self.zonelist = basic.csv2list('metadata/partialzonelist.csv')
		self.testlist = ['RM-4132']
		self.actuNames = ActuatorNames()
		self.sensorNames = SensorNames()
	
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
		filenameList = list()
		filenameList.append('data/2015-09-28T1.pkl')
		filenameList.append('data/2015-09-26T1.pkl')

		dataList = list()
		for filename in filenameList:
			with open(filename, 'rb') as fp:
				data = pickle.load(fp)
			dataList.append(self.arrange_data(data['RM-4132']))
		dataDict = self.merge_data(dataList[0], dataList[:-1])

		for key, data in dataDict.iteritems():
			print key
			self.fit_data(data[key], data.drop(key,axis=1))
	
	
	def fit_data(self, y, xs):
		svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
		y_rbf = svr_rbf.fit(xs, y).predict(xs)
		fig = plt.figure()
		ax = fig.add_subplot(111,projection='3d')
		ax.scatter(xs[xs.keys()[0]],xs[xs.keys()[0]],y,c='k')
		plt.show()
		pass
