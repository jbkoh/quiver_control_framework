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
from collections import OrderedDict, defaultdict
import pprint


class FindDep:
	zonelist = None
	testlist = None
	actuNames = None
	sensorNames = None
	bdm = None
	anal = None
	outputfile = None
	#allKeys = ['cs', 'oc', 'acs', 'ahs', 'zt', 'cc', 'hc', 'rvc', 'cmf', 'ocm', 'ohf', 'asfsp', 'asf', 'dp', 'dc']
	allKeys = ['cs', 'oc', 'cc', 'hc', 'rvc', 'asfsp','dc']
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
		#output['acs'] = acs
		#output['ahs'] = ahs
		#output['zt'] = zt
		output['cc'] = cc
		output['hc'] = hc
		output['rvc'] = rvc
		#output['cmf'] = cmf
		#output['ocm'] = ocm
		#output['ohf'] = ohf
		output['asfsp'] = asfsp
		#output['asf'] = asf
		#output['dp'] = dp
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
				if True in (abs(actuDiff[tp-timedelta(minutes=7):tp+timedelta(minutes=10)])>threshold).values:
					depCnt += 1
		if entireChgCnt==0:
			corrVal = None
		else:
			corrVal = float(depCnt) / float(entireChgCnt)
		descendCorr = corrVal


		return (descendCorr, ascendCorr)

	def calc_corr_cnt(self, controlledData, uncontrolledData):
		controlledMin = min(controlledData)
		controlledMax = max(controlledData)
		controlledThre = (controlledMax-controlledMin)*0.1
#		controlledThre = 0
		uncontrolledMin = min(uncontrolledData)
		uncontrolledMax = max(uncontrolledData)
		uncontrolledThre = (uncontrolledMax-uncontrolledMin)*0.05
#		uncontrolledThre = 0
		controlledDiff = controlledData.diff().fillna(0)
		uncontrolledDiff = uncontrolledData.diff().fillna(0)
		depCnt = 0
		entireChgCnt = 0
		
		depCnt = 0
		entireChgCnt = 0
		for tp, val in controlledDiff.iterkv():
			if abs(val) >controlledThre:
				entireChgCnt += 1
				threshold = np.std(uncontrolledData[tp-timedelta(minutes=12):tp])*2
#				if True in (abs(uncontrolledDiff[tp-timedelta(minutes=2):tp+timedelta(minutes=10)])>uncontrolledThre).values:
				if True in (abs(uncontrolledDiff[tp-timedelta(minutes=7):tp+timedelta(minutes=10)])>threshold).values:
					depCnt += 1
		return (entireChgCnt, depCnt)

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
			if actu=='hc':
				pass
			corrDict[actu] = self.calc_corr(dataDict[targetActu], dataDict[actu])
		print repr(corrDict)
		return corrDict

	def calc_dep(self, filelist, controlledKey):
		controlledChangeDict = defaultdict(float)
		depChangeDict = defaultdict(float)
		keylist = deepcopy(self.allKeys)
		keylist.remove(controlledKey)
		for filename in filelist:
			print filename
			with open(filename, 'rb') as fp:
				dataDict = self.arrange_data(pickle.load(fp))
			controledData = dataDict[controlledKey]
			del dataDict[controlledKey]
			for key in keylist:
				print key
				(contCnt, uncontCnt) = self.calc_corr_cnt(controledData, dataDict[key])
				controlledChangeDict[key] += contCnt
				depChangeDict[key] += uncontCnt
		probDict = dict()
		for key in self.allKeys:
			try:
				probDict[key] = depChangeDict[key]/controlledChangeDict[key]
			except:
				probDict[key] = 0
		return probDict

	def dep_analysis_all(self):
		zonelist = ['RM-2108', 'RM-2112', 'RM-2118', 'RM-2226', 'RM-2230']
		filedictdictlist = dict()
		filedictdictlist['RM-2108'] = defaultdict(list)
		filedictdictlist['RM-2108']['cs'].append('data/dep/dep_cs_2108_1015.pkl')
		filedictdictlist['RM-2108']['cs'].append('data/dep/dep_cs_2108_1016.pkl')
		filedictdictlist['RM-2108']['cs'].append('data/dep/dep_cs_2108_1017.pkl')
		filedictdictlist['RM-2108']['oc'].append('data/dep/dep_oc_2108_1015.pkl')
		filedictdictlist['RM-2108']['oc'].append('data/dep/dep_oc_2108_1016.pkl')
		filedictdictlist['RM-2108']['oc'].append('data/dep/dep_oc_2108_1017.pkl')
		filedictdictlist['RM-2108']['cc'].append('data/dep/dep_cc_2108_1015.pkl')
		filedictdictlist['RM-2108']['cc'].append('data/dep/dep_cc_2108_1016.pkl')
		filedictdictlist['RM-2108']['oc'].append('data/dep/dep_cc_2108_1017.pkl')
		filedictdictlist['RM-2108']['hc'].append('data/dep/dep_hc_2108_1015.pkl')
		filedictdictlist['RM-2108']['asfsp'].append('data/dep/dep_asfsp_2108_1018.pkl')

		filedictdictlist['RM-2112'] = defaultdict(list)
		filedictdictlist['RM-2112']['cs'].append('data/dep/dep_cs_2112_1015.pkl')
		filedictdictlist['RM-2112']['cs'].append('data/dep/dep_cs_2112_1016.pkl')
		filedictdictlist['RM-2112']['cs'].append('data/dep/dep_cs_2112_1017.pkl')
		filedictdictlist['RM-2112']['oc'].append('data/dep/dep_oc_2112_1015.pkl')
		filedictdictlist['RM-2112']['oc'].append('data/dep/dep_oc_2112_1016.pkl')
		filedictdictlist['RM-2112']['oc'].append('data/dep/dep_oc_2112_1017.pkl')
		filedictdictlist['RM-2112']['cc'].append('data/dep/dep_cc_2112_1015.pkl')
		filedictdictlist['RM-2112']['cc'].append('data/dep/dep_cc_2112_1016.pkl')
		filedictdictlist['RM-2112']['oc'].append('data/dep/dep_cc_2112_1017.pkl')
		filedictdictlist['RM-2112']['hc'].append('data/dep/dep_hc_2112_1015.pkl')
		filedictdictlist['RM-2112']['asfsp'].append('data/dep/dep_asfsp_2112_1018.pkl')

		filedictdictlist['RM-2118'] = defaultdict(list)
		filedictdictlist['RM-2118']['cs'].append('data/dep/dep_cs_2118_1015.pkl')
		filedictdictlist['RM-2118']['cs'].append('data/dep/dep_cs_2118_1016.pkl')
		filedictdictlist['RM-2118']['cs'].append('data/dep/dep_cs_2118_1017.pkl')
		filedictdictlist['RM-2118']['oc'].append('data/dep/dep_oc_2118_1015.pkl')
		filedictdictlist['RM-2118']['oc'].append('data/dep/dep_oc_2118_1016.pkl')
		filedictdictlist['RM-2118']['oc'].append('data/dep/dep_oc_2118_1017.pkl')
		filedictdictlist['RM-2118']['cc'].append('data/dep/dep_cc_2118_1015.pkl')
		filedictdictlist['RM-2118']['cc'].append('data/dep/dep_cc_2118_1016.pkl')
		filedictdictlist['RM-2118']['oc'].append('data/dep/dep_cc_2118_1017.pkl')
		filedictdictlist['RM-2118']['hc'].append('data/dep/dep_hc_2118_1015.pkl')
		filedictdictlist['RM-2118']['asfsp'].append('data/dep/dep_asfsp_2118_1018.pkl')

		filedictdictlist['RM-2226'] = defaultdict(list)
		filedictdictlist['RM-2226']['cs'].append('data/dep/dep_cs_2226_1012.pkl')
		filedictdictlist['RM-2226']['oc'].append('data/dep/dep_oc_2226_1012.pkl')
		filedictdictlist['RM-2226']['cc'].append('data/dep/dep_cc_2226_1012.pkl')
		filedictdictlist['RM-2226']['cc'].append('data/dep/dep_cc_2226_1014.pkl')
		filedictdictlist['RM-2226']['hc'].append('data/dep/dep_hc_2226_1012.pkl')
		filedictdictlist['RM-2226']['hc'].append('data/dep/dep_hc_2226_1013.pkl')
		filedictdictlist['RM-2226']['asfsp'].append('data/dep/dep_asfsp_2226_1012.pkl')
		filedictdictlist['RM-2226']['asfsp'].append('data/dep/dep_asfsp_2226_1013.pkl')
		filedictdictlist['RM-2226']['dc'].append('data/dep/dep_dc_2226_1012.pkl')
		filedictdictlist['RM-2226']['dc'].append('data/dep/dep_dc_2226_1013.pkl')
		#filedictdictlist['RM-2226']['asfsp'].append('data/dep/dep_asfsp_2226_1018.pkl')

		filedictdictlist['RM-2230'] = defaultdict(list)
		filedictdictlist['RM-2230']['cs'].append('data/dep/dep_cs_2230_1012.pkl')
		filedictdictlist['RM-2230']['oc'].append('data/dep/dep_oc_2230_1012.pkl')
		filedictdictlist['RM-2230']['cc'].append('data/dep/dep_cc_2230_1012.pkl')
		filedictdictlist['RM-2230']['cc'].append('data/dep/dep_cc_2230_1014.pkl')
		filedictdictlist['RM-2230']['hc'].append('data/dep/dep_hc_2230_1012.pkl')
		filedictdictlist['RM-2230']['hc'].append('data/dep/dep_hc_2230_1013.pkl')
		filedictdictlist['RM-2230']['asfsp'].append('data/dep/dep_asfsp_2230_1012.pkl')
		filedictdictlist['RM-2230']['asfsp'].append('data/dep/dep_asfsp_2230_1013.pkl')
		filedictdictlist['RM-2230']['dc'].append('data/dep/dep_dc_2230_1012.pkl')
		filedictdictlist['RM-2230']['dc'].append('data/dep/dep_dc_2230_1013.pkl')
		#filedictdictlist['RM-2230']['asfsp'].append('data/dep/dep_asfsp_2230_1018.pkl')

		probDict = dict()
		pprinter = pprint.PrettyPrinter(indent=4)
		excelWriter = pd.ExcelWriter(self.outputfile)
		for zone, filedictlist in filedictdictlist.iteritems():
			print zone
			zoneProb = self.dep_analysis_rep(zone, filedictlist)
			probDict[zone] = zoneProb
			probDF = pd.DataFrame.from_dict(zoneProb,'columns').transpose()
			pprinter.pprint(zoneProb)
			probDF.to_excel(excelWriter, 'Sheet_'+zone.replace('RM-',''))
		pprinter.pprint(probDict)

	def dep_analysis_rep(self, zone, filedictlist):
		probDict = dict()
		for key, filelist in filedictlist.iteritems():
			print "========================================master key: ", key
			probDict[key] = self.calc_dep(filelist, key)
		return probDict

	def dep_analysis(self, zone=None, filedictlist=None):
		filenameDict = OrderedDict()
		
		filenameDict['cs'] = ('data/dep_all_2226_1012.pkl')
		filenameDict['oc'] = ('data/dep_all_2226_1012.pkl')
		filenameDict['cc'] = ('data/dep_cc_3256_1005.pkl')
		filenameDict['hc'] = ('data/dep_hc_2208_1012.pkl')
		filenameDict['asfsp'] = ('data/dep_all_2226_1012.pkl')
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

