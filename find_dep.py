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
from collections import OrderedDict


class FindDep:
	zonelist = None
	testlist = None
	actuNames = None
	sensorNames = None
	bdm = None
	anal = None
	outputfile = None
	allKeys = ['cs', 'oc', 'acs', 'ahs', 'zt', 'cc', 'hc', 'rvc', 'cmf', 'ocm', 'ohf', 'asfsp', 'asf', 'dp', 'dc']
	def __init__ (self):
		self.zonelist = basic.csv2list('metadata/partialzonelist.csv')
		self.actuNames = ActuatorNames()
		self.sensorNames = SensorNames()
		self.bdm = BDWrapper()
		self.anal = Analyzer()
		self.outputfile = 'result/dep_result.xlsx'

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
		rvc = rawData[self.actuNames.reheatValveCommand]
		cmf = rawData[self.actuNames.coolingMaxFlow]
		ohf = rawData[self.actuNames.occupiedHeatingFlow]
		ocm = rawData[self.actuNames.occupiedCoolingMinimumFlow]
		asfsp = rawData[self.actuNames.actualSupplyFlowSP]
		asf = rawData[self.sensorNames.actualSupplyFlow]
		dc = rawData[self.actuNames.damperCommand]
		dp = rawData[self.sensorNames.damperPosition]
		newcs = cs + wcad
		acs_diff = acs - zt

		output = dict()
		output['cs'] = newcs
		output['oc'] = oc
		output['acs'] = acs
		output['ahs'] = ahs
		output['zt'] = zt
		output['cc'] = cc
		output['hc'] = hc
		output['rvc'] = rvc
		output['cmf'] = cmf
		output['ocm'] = ocm
		output['ohf'] = ohf
		output['asfsp'] = asfsp
		output['asf'] = asf
		output['dp'] = dp
		output['dc'] = dc

		return output


	def calc_corr(self, targetActu, actu):
		targetMin = min(targetActu)
		targetMax = max(targetActu)
		targetThre = (targetMax-targetMin)*0.1
#		targetThre = 0
		actuMin = min(actu)
		actuMax = max(actu)
		actuThre = (actuMax-actuMin)*0.05
#		actuThre = 0
		targetDiff = targetActu.diff().fillna(0)
		actuDiff = actu.diff().fillna(0)
		depCnt = 0
		entireChgCnt = 0

		ascendCorr =  0 # P(A|B) when A->B
		for tp, val in actuDiff.iterkv():
			if val >actuThre:
				entireChgCnt += 1
				if True in (abs(targetDiff[tp-timedelta(minutes=10):tp+timedelta(minutes=2)])>targetThre).values:
					depCnt += 1
		if entireChgCnt==0:
			corrVal = None
		else:
			corrVal = float(depCnt) / float(entireChgCnt)
		ascendCorr = corrVal
		
		
		descendCorr = 0 # P(B|A) when A->B
		depCnt = 0
		entireChgCnt = 0
		for tp, val in targetDiff.iterkv():
			if val >targetThre:
				entireChgCnt += 1
				threshold = np.std(actu[tp-timedelta(minutes=12):tp])
#				if True in (abs(actuDiff[tp-timedelta(minutes=2):tp+timedelta(minutes=10)])>actuThre).values:
				if True in (abs(actuDiff[tp-timedelta(minutes=2):tp+timedelta(minutes=10)])>threshold).values:
					depCnt += 1
		if entireChgCnt==0:
			corrVal = None
		else:
			corrVal = float(depCnt) / float(entireChgCnt)
		descendCorr = corrVal


		return (descendCorr, ascendCorr)

	def find_lower_actuators(self, filename, targetActu):
		with open(filename, 'rb') as fp:
			dataDict = self.arrange_data(pickle.load(fp))

		diffDict = dict()
		minDict = dict()
		maxDict = dict()
		corrDict = dict()
		for key in self.allKeys:
			corrDict[key] = (None,None)
		
		for actu, data in dataDict.iteritems():
			minDict[actu] = min(data)
			maxDict[actu] = max(data)
			diffDict[actu] = data.diff().fillna(0)

		keyList = dataDict.keys()
		keyList.remove(targetActu)
		for actu in keyList:
			corrDict[actu] = self.calc_corr(dataDict[targetActu], dataDict[actu])
		print repr(corrDict)
		return corrDict

	def dep_analysis(self):
		filenameDict = OrderedDict()
		filenameDict['cs'] = ('data/dep_cs_3142_1005.pkl')
#		filenameDict['oc'] = ('data/dep_oc_3152_1005.pkl')
		filenameDict['oc'] = ('data/dep_oc_2108_1008.pkl')
		filenameDict['cc'] = ('data/dep_cc_3256_1005.pkl')
		filenameDict['hc'] = ('data/dep_hc_2112_1008.pkl')
		#filenameDict['hc'] = ('data/dep_hc_3252_1005.pkl')
		filenameDict['asfsp'] = ('data/dep_asfsp_3144_1006.pkl')
		filenameDict['dc'] = ('data/dep_dc_4220_1008.pkl')

		descendOutputDF = pd.DataFrame(index=self.allKeys)
		ascendOutputDF = pd.DataFrame(index=self.allKeys)

		for actu, filename in filenameDict.iteritems():
			print actu
			print '=============', actu, '============='
			corrDict = self.find_lower_actuators(filename, actu)
			corrDF = pd.DataFrame.from_dict(corrDict,'index')
			descendOutputDF[actu] = corrDF[0]
			ascendOutputDF[actu] = corrDF[1]

		excelWriter = pd.ExcelWriter(self.outputfile)
		descendOutputDF.to_excel(excelWriter, 'Sheet1')
		ascendOutputDF.to_excel(excelWriter, 'Sheet2')

