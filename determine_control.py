import basic
from actuator_names import ActuatorNames
from sensor_names import SensorNames
import pickle

import pandas as pd
import plotter
import numpy as np
import matplotlib.pyplot as plt




class DetermineControl:
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
			if len(maxIndices)==0:
				continue
#			plotData = df[sensorList[maxIndices]]
			plotData = list()
			plotLabel = list()
			for idx in maxIndices:
				plotData.append(df[sensorList[idx]])
				plotLabel.append(sensorList[idx])

			plotter.plot_multiple_2dline(range(0,len(df[sensorList[maxIndices[0]]])), plotData, dataLabels=plotLabel)
