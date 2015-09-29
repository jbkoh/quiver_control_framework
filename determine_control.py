import basic
from actuator_names import ActuatorNames
from sensor_names import SensorNames
import pickle

import pandas as pd




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
			for zone in testlist:
				data[zone] = pd.DataFrame.from_dict(dataDict[zone])
		return pd.DataFrame.from_dict(data)

	def make_most_influence_dict(self, df):
		sensorList = df.keys()
		corrMat = df.corr()

		for sensor in sensorList:

