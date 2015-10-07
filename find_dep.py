import basic
from actuator_names import ActuatorNames
from sensor_names import SensorNames
from bd_wrapper import BDWrapper
from analyzer import Analyzer
import plotter

import pickle
import pandas as pd
import plotter
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta
from math import sqrt
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR, LinearSVR
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import LinearRegression
from copy import deepcopy
import scipy.fftpack as fftpack
from statsmodels.nonparametric.smoothers_lowess import lowess


class FindDep:
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

	def arrange_data(self, rawData):
		oc = rawData[self.actuNames.occupiedCommand]
		cs = rawData[self.actuNames.commonSetpoint]
		acs = rawData[self.actuNames.actualCoolingSetpoint]
		ahs = rawData[self.actuNames.actualHeatingSetpoint]
		zt = rawData[self.sensorNames.zoneTemperature]
		try:
			tempocc = rawData[self.actuNames.tempOccSts]
			#newoc = np.logical_or((oc-1)/2, tempocc)
			newoc = oc
			newoc[tempocc==1] = 3
		except:
			newoc = oc
		wcad = rawData[self.actuNames.warmCoolAdjust]
		cc = rawData[self.actuNames.coolingCommand]
		hc = rawData[self.actuNames.heatingCommand]
		cmf = rawData[self.actuNames.coolingMaxFlow]
		#ohf = rawData[self.actuNames.occupiedHeatingFlow]
		ocm = rawData[self.actuNames.occupiedCoolingMinimumFlow]
		asfsp = rawData[self.actuNames.actualSupplyFlowSP]
		newcs = cs + wcad
		acs_diff = acs - zt

		output = dict()
		output['oc'] = oc
		output['cs'] = newcs
		output['acs'] = acs
		output['ahs'] = ahs
		output['zt'] = zt
		output['cc'] = cc
		output['hc'] = hc
		output['cmf'] = cmf
		output['ocm'] = ocm
		output['asfsp'] = asfsp

		return output

	def calc_corr(self, targetActu, actu):
		targetMin = min(targetActu)
		targetMax = max(targetActu)
		targetThre = targetMin+(targetMax-targetMin)*0.1
		actuMin = min(actu)
		actuMax = max(actu)
		actuThre = actuMin+(actuMax-actuMin)*0.1
		targetDiff = targetActu.diff().fillna(0)
		actuDiff = actu.diff().fillna(0)
		depCnt = 0
		entireChgCnt = 0
		for tp, val in actuDiff.iterkv():
			if val >=actuThre:
				entireChgCnt += 1
				if True in (abs(targetActu[tp-timedelta(minutes=10):tp])>=targetThre).values:
					depCnt += 1
		if entireChgCnt==0:
			corrVal = None
		else:
			corrVal = depCnt / entireChgCnt
		return corrVal

	def find_lower_actuators(self, filename, targetActu):
		with open(filename, 'rb') as fp:
			dataDict = self.arrange_data(pickle.load(fp))

		diffDict = dict()
		minDict = dict()
		maxDict = dict()
		corrDict = dict()
		
		for actu, data in dataDict.iteritems():
			minDict[actu] = min(data)
			maxDict[actu] = max(data)
			diffDict[actu] = data.diff().fillna(0)

		keyList = dataDict.keys()
		keyList.remove(targetActu)
		for actu in keyList:
			corrDict[actu] = self.calc_corr(dataDict[targetActu], dataDict[actu])
		print repr(corrDict)

	def dep_analysis(self):
		filenameDict = dict()
		filenameDict['cs'] = ('data/dep_cc_3256_1005.pkl')

		for actu, filename in filenameDict.iteritems():
			self.find_lower_actuators(filename, actu)
