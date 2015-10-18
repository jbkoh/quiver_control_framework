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
from sklearn.svm import SVR, LinearSVR, OneClassSVM
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import LinearRegression
from sklearn.covariance import EllipticEnvelope
from copy import deepcopy
import scipy.fftpack as fftpack
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.stats import gaussian_kde
import matplotlib.cm as cm




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
		return date

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
	
	def shift_fill(self, data, period=1):
		if period>=0:
			return data.shift(period).fillna(method='bfill')
		else:
			return data.shift(period).fillna(method='ffill')
	
	def export_arranged_data(self, filename):
		with open(filename, 'rb') as fp:
			rawdata = pickle.load(fp)
			return self.arrange_data(rawdata)
	
	def arrange_data(self, zoneData):
		oc = zoneData[self.actuNames.occupiedCommand]
		cs = zoneData[self.actuNames.commonSetpoint]
		acs = zoneData[self.actuNames.actualCoolingSetpoint]
		ahs = zoneData[self.actuNames.actualHeatingSetpoint]
		zt = zoneData[self.sensorNames.zoneTemperature]
		try:
			tempocc = zoneData[self.actuNames.tempOccSts]
			#newoc = np.logical_or((oc-1)/2, tempocc)
			newoc = oc
			newoc[(tempocc==1).tolist()] = 3
		except:
			newoc = oc
			pass
		wcad = zoneData[self.actuNames.warmCoolAdjust]
		cc = zoneData[self.actuNames.coolingCommand]
		hc = zoneData[self.actuNames.heatingCommand]
		cmf = zoneData[self.actuNames.coolingMaxFlow]
		#ohf = zoneData[self.actuNames.occupiedHeatingFlow]
		ocm = zoneData[self.actuNames.occupiedCoolingMinimumFlow]
		const = pd.Series(data=np.ones(len(oc)), index=oc.index)
		asfsp = zoneData[self.actuNames.actualSupplyFlowSP]
		asf = zoneData[self.sensorNames.actualSupplyFlow]
		dc = zoneData[self.actuNames.damperCommand]
		#dp = zoneData[self.sensorNames.damperPosition]
		zt_lag1 = self.shift_fill(zt,3)
		zt_lag2 = self.shift_fill(zt,6)
		zt_lag3 = self.shift_fill(zt,9)
		zt_lag4 = self.shift_fill(zt,12)
		zt_lag5 = self.shift_fill(zt,15)
		acs_lag1 = self.shift_fill(acs,3)
		acs_lag2 = self.shift_fill(acs,6)
		acs_lag3 = self.shift_fill(acs,9)
		acs_lag4 = self.shift_fill(acs,12)
		acs_lag5 = self.shift_fill(acs,15)
		cc_lag1 = self.shift_fill(cc,3)
		cc_lag2 = self.shift_fill(cc,6)
		cc_lag3 = self.shift_fill(cc,9)
		mincc = deepcopy(cc)
		mincc[:]=0
		maxcc = deepcopy(cc)
		maxcc[:]=100
		newcs = cs + wcad
		acs_diff = acs - zt
		ahs_diff = zt - ahs
		acs_diff_diff = acs_diff.diff().fillna(method='bfill')
		acs_diff_lag1 = self.shift_fill(acs_diff,3)
		acs_diff_lag2 = self.shift_fill(acs_diff,6)
		acs_diff_lag3 = self.shift_fill(acs_diff,9)
		acs_diff_lag4 = self.shift_fill(acs_diff,4)
		acs_diff_lag5 = self.shift_fill(acs_diff,5)
		acs_diff_lag6 = self.shift_fill(acs_diff,6)

		#acsDF = pd.DataFrame({'acs':acs, 'cs':cs, 'oc':newoc, 'wcad':wcad, 'const':const})
		acsDF = pd.DataFrame({'acs':acs, 'cs':newcs, 'oc':newoc})
		#ahsDF = pd.DataFrame({'ahs':ahs, 'cs':cs, 'oc':oc, 'tempocc':tempocc, 'wcad':wcad})
		ahsDF = pd.DataFrame({'ahs':ahs, 'cs':newcs, 'oc':newoc})


		#ccDF = pd.DataFrame({'cc':cc, 'zt':zt, 'acs':acs, 'maxcc':maxcc, 'mincc':mincc})
		ccDF = pd.DataFrame({'cc':cc, 'zt':zt, 'acs':acs, 'zt_lag1':zt_lag1, 'zt_lag2':zt_lag2, 'zt_lag3':zt_lag3,'acs_lag1':acs_lag1,'acs_lag2':acs_lag2, 'acs_lag3':acs_lag3, 'maxcc':maxcc, 'mincc':mincc, 'acsdiff':acs_diff, 'zt_lag4':zt_lag4, 'zt_lag5':zt_lag5, 'acs_lag4':acs_lag4, 'acs_lag5':acs_lag5, 'oc':newoc, 'acs_diff_lag1':acs_diff_lag1, 'acs_diff_lag2':acs_diff_lag2, 'acs_diff_lag3':acs_diff_lag3})
		#ccDF = pd.DataFrame({'cc':cc, 'zt':zt, 'acs':acs, 'acs_diff':acs_diff, 'acs_diff_diff':acs_diff_diff, 'acs_diff_lag1':acs_diff_lag1, 'acs_diff_lag2':acs_diff_lag2, 'acs_diff_lag3':acs_diff_lag3, 'acs_diff_lag4':acs_diff_lag4, 'acs_diff_lag5':acs_diff_lag5, 'acs_i':acs_i, 'zt_i':zt_i, })
		hcDF = pd.DataFrame({'hc':hc, 'zt':zt, 'ahs':ahs, 'oc':newoc, 'ahs_diff':ahs_diff})
		asfspDF = pd.DataFrame({'asfsp':asfsp, 'cc':cc, 'oc':newoc, 'hc':hc, 'ocm':ocm, 'cmf':cmf})
		#asfspDF = pd.DataFrame({'asfsp':asfsp, 'cc':cc, 'hc':hc, 'ocm':ocm, 'cmf':cmf})
		dcDF = pd.DataFrame({'dc':dc, 'asf':asf, 'asfsp':asfsp})
		output = dict()
		output['acs'] = acsDF
		output['ahs'] = ahsDF
		output['cc'] = ccDF
		output['hc'] = hcDF
		output['asfsp'] = asfspDF
		output['dc'] = dcDF
		return output

	def conditional_filter(self, dataDict, targetType, conditionList):
		filtered = dataDict
		for (key, val, condType) in conditionList:
			if condType=='equal':
				filtered = filtered[np.logical_and(filtered[key]<=val+val*0.01, filtered[key]>=val-val*0.01)]
			elif condType=='less':
				filtered = filtered[filtered[key]<=val]
			else:
				print "wrong conditional type"
				return None
		
		return filtered

		#for data in filtered.drop(key=targetType, axis=1):
		#	plt.scatter(filtered[targetType], data)
		#	plt.show()

	def filelist_to_dict(self, filenameList):
		dataList = list()
		for idx, filename in enumerate(filenameList):
			with open(filename,'rb') as fp:
				rawDataDict = pickle.load(fp)
				arrangedData = self.arrange_data(rawDataDict)
				dataList.append(arrangedData)
		if len(dataList)==1:
			dataDict = dataList[0]
		else:
			dataDict = self.merge_data(dataList[0], dataList[:-1])
		return dataDict

	def simple_relationship(self, filenameList, key, conditionList):
		dataDict = self.filelist_to_dict(filenameList)
		data = dataDict[key]
		filtered = self.conditional_filter(data, key, conditionList)
		for pointType, data in filtered.drop(key, axis=1).iterkv():
			plt.scatter(data, filtered[key])
			plt.title(pointType)
			plt.show()


	def top_part_reg(self):
		testFileList = ['data/testmonth_2236_0701.pkl']
		print "One day----------------------------"
		fileList = ['data/oneday_2236_0804.pkl']
		self.partial_regression(fileList, 'asfsp', [('oc',3,'equal'), ('hc',10,'less')], testFileList)
		print "One month----------------------------"
		fileList = ['data/onemonth_2236_0801.pkl']
		self.partial_regression(fileList, 'asfsp', [('oc',3,'equal'), ('hc',10,'less')], testFileList)
		print "Half year----------------------------"
		fileList = ['data/halfyear_2236_0401.pkl']
		self.partial_regression(fileList, 'asfsp', [('oc',3,'equal'), ('hc',10,'less')], testFileList)
		print "One year----------------------------"
		fileList = ['data/oneyear_2236_0801.pkl']
		self.partial_regression(fileList, 'asfsp', [('oc',3,'equal'), ('hc',10,'less')], testFileList)


	def partial_regression(self, fileList, key, conditionList, testFileList):
		dataDict = self.filelist_to_dict(fileList)
		dataDF = dataDict[key]
		filteredData = self.conditional_filter(dataDF, key, conditionList)
		testDict = self.filelist_to_dict(testFileList)
		testDF = testDict[key]
		filteredTestData = self.conditional_filter(testDF, key, conditionList)
		for pointType, data in filteredData.drop(key, axis=1).iterkv():
			print pointType
			model = LinearRegression()
			df = pd.DataFrame({pointType:data})
			fitted = model.fit(df, filteredData[key])
			try:
				print xs.keys()
				print model.coef_
				pass
			except:
				pass
			yTest = fitted.predict(pd.DataFrame({pointType:filteredTestData[pointType]}))
			yLearn = fitted.predict(pd.DataFrame({pointType:data}))

			learnRmse = sqrt(mean_squared_error(filteredData[key], yLearn))
			testRmse = sqrt(mean_squared_error(filteredTestData[key], yTest))
			normRmse = testRmse/np.mean(yTest)
			print 'Learn RMSE:\t', learnRmse
			print 'Test RMSE:\t', testRmse
		
			



	def all_relationship(self):
		#filenameList = ['data/oneyear_3148_0701.pkl']
		#filenameList = ['data/onemonth_3148_0801.pkl']
		#filenameList = ['data/onemonth_3148_0101.pkl']
		filenameList = ['data/oneday_2230_0801.pkl']
		#filenameList.append('data/oneyear_3256_0701.pkl')
		print 'hc'
		self.simple_relationship(filenameList, 'hc', [('oc',3)])
		print 'asfsp'
		self.simple_relationship(filenameList, 'asfsp', [('oc',3)])
		print 'acs'
		self.simple_relationship(filenameList, 'acs', [('oc',3)])
		print 'cc'
		#self.simple_relationship(filenameList, 'cc', [('oc',3), ('acs', 74)])
		self.simple_relationship(filenameList, 'cc', [('oc',3)])

#		filenameList = ['data/onemonth_3256_0901.pkl']
#		#filenameList.append('data/oneyear_3256_0701.pkl')
#		self.simple_relationship(filenameList, 'asfsp', [('oc',3)])
		
#		filenameList = ['data/oneyear_3256_0701.pkl']
#		self.simple_relationship(filenameList, 'asfsp', [('oc',1)])
		
#		filenameList = ['data/reg_safsp_3256_1006.pkl']
#		self.simple_relationship(filenameList, 'asfsp', [('oc',3),('hc',0)])
		
#		filenameList = ['data/oneyear_3256_0701.pkl']
#		self.simple_relationship(filenameList, 'dc', [])

	def merge_data(self, data1, dataList):
		dataDict = dict()
		for key in data1.iterkeys():
			data1[key].index = range(0,len(data1[key]))
			idxLen = len(data1[key])
#			data1[key] = pd.concat([df1, dataList[key]])
			for data in dataList:
				data[key].index = range(idxLen,idxLen+len(data[key]))
				idxLen = idxLen + len(data[key])
				dataDict[key] = data1[key].append(data[key], ignore_index=True)
		return dataDict

	def lpf(self, data):
		filtered = deepcopy(data)
		lpfLen = 20
		for i in range(0,lpfLen):
			filtered = filtered + self.shift_fill(data,i)
			filtered = filtered + self.shift_fill(data,-i)
		filtered = filtered / (lpfLen*2+1)
		return filtered

	def fit_all_types(self):
		print "=======================ASFSP STARTS (MIXED)==========================="
		ccLearnFiles = list()
		ccTestFiles = list()
		ccAuxFiles = list()
		ccAuxFiles.append('data/onemonth_3256_0901.pkl')
		ccLearnFiles.append('data/reg_safsp_3256_1006.pkl')
		ccTestFiles.append('data/oneyear_3256_0701.pkl')
		self.fit_for_a_type(ccLearnFiles, ccTestFiles, 'asfsp',auxFileList=ccAuxFiles)
		print "=======================ACS and AHS STARTS (w/o control)==========================="
		acsahsLearnFiles = []
		acsahsAuxFiles = None
		acsahsTestFiles = []
		acsahsLearnFiles.append('data\onemonth_3256_0901.pkl')

		#acsahsLearnFiles.append('data\oneday_2146_1004.pkl')
		acsahsTestFiles.append('data\oneyear_3256_0701.pkl')
		#acsahsTestFiles.append('data\oneyear_2146_0101.pkl')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'acs', auxFileList=acsahsAuxFiles)
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'ahs')
		
		print "=======================ACS and AHS STARTS (MIXED)==========================="
		acsahsLearnFiles = []
		acsahsAuxFiles = []
		acsahsTestFiles = []
		acsahsAuxFiles.append('data\onemonth_3256_0901.pkl')
		acsahsLearnFiles.append('data\reg_cs_3256_1010.pkl')

		#acsahsLearnFiles.append('data\oneday_2146_1004.pkl')
		acsahsTestFiles.append('data\oneyear_3256_0701.pkl')
		#acsahsTestFiles.append('data\oneyear_2146_0101.pkl')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'acs', auxFileList=acsahsAuxFiles)
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'ahs')
		
		print "=======================CC STARTS (MIXED)==========================="
		ccLearnFiles = list()
		ccTestFiles = list()
		ccAuxFiles = list()
#		ccLearnFiles.append('data\onemonth_2150_0820.pkl')
		ccAuxFiles.append('data\onemonth_3152_0801.pkl')
		ccLearnFiles.append('data/reg_cc_3152_1001.pkl')
#		ccTestFiles.append('data\oneday_2150_0914.pkl')
		ccTestFiles.append('data/oneyear_3152_0101.pkl')
		self.fit_for_a_type(ccLearnFiles, ccTestFiles, 'cc', auxFileList=ccAuxFiles)
		

		print "=======================ASFSP STARTS (w/o CONTROL)==========================="
		ccLearnFiles = list()
		ccTestFiles = list()
		ccLearnFiles.append('data/onemonth_3256_0901.pkl')
		ccTestFiles.append('data/oneyear_3256_0701.pkl')
		self.fit_for_a_type(ccLearnFiles, ccTestFiles, 'asfsp')

		
		
		print "=======================ASFSP STARTS (w/ CONTROL)==========================="
		ccLearnFiles = list()
		ccTestFiles = list()
		ccLearnFiles.append('data/reg_safsp_3256_1006.pkl')
		ccTestFiles.append('data/oneyear_3256_0101.pkl')
		self.fit_for_a_type(ccLearnFiles, ccTestFiles, 'asfsp')

		print "=======================ACS and AHS STARTS (MIXED)==========================="
		acsahsLearnFiles = []
		acsahsAuxFiles = []
		acsahsTestFiles = []
		acsahsAuxFiles.append('data\onemonth_2142_0801.pkl')
		acsahsLearnFiles.append('data\oneday_2142_1004.pkl')

		#acsahsLearnFiles.append('data\oneday_2146_1004.pkl')
		acsahsTestFiles.append('data\oneyear_2142_0101.pkl')
		#acsahsTestFiles.append('data\oneyear_2146_0101.pkl')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'acs', auxFileList=acsahsAuxFiles)
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'ahs')
		
		print "=======================ACS and AHS STARTS (w/o CONTROL)==========================="
		acsahsLearnFiles = []
		acsahsLearnFiles.append('data\onemonth_2142_0801.pkl')
		#acsahsLearnFiles.append('data\oneday_2146_1004.pkl')
		acsahsTestFiles = []
		acsahsTestFiles.append('data\oneyear_2142_0101.pkl')
		#acsahsTestFiles.append('data\oneyear_2146_0101.pkl')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'acs')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'ahs')

		print "=======================ACS and AHS STARTS (w/ CONTROL)==========================="
		acsahsLearnFiles = []
		acsahsLearnFiles.append('data\oneday_2142_1004.pkl')
		#acsahsLearnFiles.append('data\oneday_2146_1004.pkl')
		acsahsTestFiles = []
		acsahsTestFiles.append('data\oneyear_2142_0101.pkl')
		#acsahsTestFiles.append('data\oneyear_2146_0101.pkl')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'acs')
		self.fit_for_a_type(acsahsLearnFiles, acsahsTestFiles, 'ahs')

		
		
		print "=======================CC STARTS (w/o CONTROL)==========================="
		ccLearnFiles = list()
		ccTestFiles = list()
#		ccLearnFiles.append('data\onemonth_2150_0820.pkl')
		ccLearnFiles.append('data\onemonth_3152_0801.pkl')
#		ccTestFiles.append('data\oneday_2150_0914.pkl')
		ccTestFiles.append('data/oneyear_3152_0101.pkl')
		self.fit_for_a_type(ccLearnFiles, ccTestFiles, 'cc')
		
		print "=======================CC STARTs (w/ CONTROL)==========================="
		ccLearnFiles = []
		ccLearnFiles.append('data/reg_cc_3152_1001.pkl')
		ccTestFiles = list()
		ccTestFiles.append('data/oneyear_3152_0101.pkl')
		self.fit_for_a_type(ccLearnFiles, ccTestFiles, 'cc')

	def remove_same_rows(self, df):
		newDF = pd.DataFrame(df[0])
		for row in df.iterrows():
			if not row[1] in newDF:
					newDF.append(row[1])
		return newDF


	def compress_aux_data(self, auxDataDict, dataLen):
		key = 'acs'
#		#model = OneClassSVM(kernel='linear')
#		model = EllipticEnvelope()
#		fitted = model.fit(auxDataDict.drop(key='acs', axis=1), auxDataDict['acs'])
##		decFunc = model.decision_function(auxDataDict)
#		output = fitted.predict(auxDataDict.drop(key='acs',axis=1))
#		print len(output[output==-1])
#		np.savetxt('result/svcresult.csv',output,delimiter='\n')
		model = LinearRegression()
		fitted = model.fit(auxDataDict.drop(key, axis=1), auxDataDict[key])
		predicted = fitted.predict(auxDataDict.drop(key, axis=1))
		predDiff = abs(auxDataDict[key]-predicted)
		sortedPredDiff = predDiff.sort(ascending=False)
		seledtedSamples = auxDataDict[0:dataLen]
		return selectedSamples
	
	def duplicate_data(self, data, num):
		for key, df in data.iteritems():
#			for i in range(0, num/len(df)-1):
				#df = df.append(df.iloc[i-len(df)], ignore_index=True)
#				df = df.append(df)
#			data[key] = df
			df = df.append([df]*(num/len(df)-1), ignore_index=True)
			data[key] = df
		return data

	
	def plot_rawdata(self, y, xs):
		for key, x in xs.iterkv():
			xmin = min(x)
			ymin = min(y)
			ymax = max(y)
			xmax = max(x)
			ynum = 10
			xnum = 10
			ygran = (ymax-ymin)/ynum
			xgran = (xmax-xmin)/xnum
			if (ymax-ymin)<=10:
				ynum = int(ymax-ymin)+1
				ygran = 1
			if (xmax-xmin)<=10:
				xnum = xmax-xmin
				xnum = int(xmax-xmin)+1
				xgran = 1
			tmap = np.ndarray([ynum, xnum], offset=0)
			for i in range(0,xnum):
				for j in range(0,ynum):
					tmap[j,i] = 0
			for idx, val in y.iterkv():
				#xidx = round((x[idx]-xmin)/xgran)
				xidx = (int(x[idx])-int(xmin))/xgran
				yidx = (int(val)-int(ymin))/ygran
				if xidx<0:
					xidx = 0
				if yidx<0:
					yidx = 0
				if xidx>=xnum:
					xidx = xnum-1
				if yidx>=ynum:
					yidx = ynum-1

				tmap[yidx, xidx] +=1 

			
			#plt.scatter(x,y,z,s=50,edgecolor='')
			#plt.title(key)
			#plt.show()
#			fig, ax = plt.subplots(1,1)
			print "xmin: ", xmin, "xmax: ", max(x)
			print "ymin: ", ymin, 'ymax: ', max(y)
			ytickRange = np.arange(0,ynum+1)
			#plotter.plot_colormap_upgrade(tmap, (12,8), key, 'Y', 'density', cm.Blues, ytickRange, [], xmin=int(xmin), xmax=int(xmax), ymin=int(ymin), ymax=int(ymax), ygran=ygran, xgran=xgran)
			plotter.plot_colormap_upgrade(tmap, (12,8), key, 'Y', 'density', cm.Blues, ytickRange, [])

	def fit_for_a_type(self, filenameList, testfilenameList, key, auxFileList=None ):
#		#rawDataDict = self.anal.receive_entire_sensors_notstore(datetime(2015,9,29),datetime(2015,9,30,6))
#		filenameList = list()
#		testfilenameList = list()
#		#testfilenameList.append('data\oneweek_4152_0714.pkl')
#		#testfilenameList.append('data\oneday_2148_0820.pkl')
#		#testfilenameList.append('data\oneweek_2142_0801.pkl')
#		testfilenameList.append('data\oneyear_2146_0101.pkl')
#		
#		#testfilenameList.append('data\oneweek_2150_0920.pkl')
#		#filenameList.append('data\oneday_2234_1004.pkl')
#		#filenameList.append('data\oneday_4150_1004.pkl')
#		filenameList.append('data\oneday_2146_1004.pkl')
#		
#
#		#filenameList.append('data\oneyear_2150_0101.pkl')
#
#		#filenameList.append('data\oneweek_4152_0714.pkl')
#		#filenameList.append('data\oneweek_2148_0714.pkl')
#		#filenameList.append('data\onemonth_2150_0820.pkl')

#		for idx, filename in enumerate(filenameList):
#			with open(filename, 'rb') as fp:
#				data = pickle.load(fp)
#			if idx==0:
#				dataList.append(self.arrange_data(data['RM-4132']))
#			else:
#				dataList.append(self.arrange_data(data['RM-2108']))

		#for zone in self.testlist:
		#	dataList.append(self.arrange_data(rawDataDict[zone]))
		auxDataList = list()
		if auxFileList!=None:
			for idx, filename in enumerate(auxFileList):
				with open(filename,'rb') as fp:
					rawDataDict = pickle.load(fp)
					arrangedData = self.arrange_data(rawDataDict)
					auxDataList.append(arrangedData)
			if len(auxDataList)==1:
				auxDataDict = auxDataList[0]
			else:
				auxDataDict = self.merge_data(auxDataList[0], auxDataList[:-1])
		
		dataList = list()
		for idx, filename in enumerate(filenameList):
			with open(filename,'rb') as fp:
				rawDataDict = pickle.load(fp)
				arrangedData = self.arrange_data(rawDataDict)
				dataList.append(arrangedData)
		if len(dataList)==1:
			dataDict = dataList[0]
		else:
			dataDict = self.merge_data(dataList[0], dataList[:-1])

		if auxFileList!=None:
			dataDict = self.duplicate_data(dataDict, len(auxDataDict[auxDataDict.keys()[0]]))


		testDataList = list()
		for idx, filename in enumerate(testfilenameList):
			with open(filename,'rb') as fp:
				rawDataDict = pickle.load(fp)
				testDataList.append(self.arrange_data(rawDataDict))
		if len(testDataList)==1:
			testDataDict = testDataList[0]
		else:
			testDataDict=  self.merge_data(testDataList[0], testDataList[:-1])

		if auxFileList != None:
			data = dataDict[key].append(auxDataDict[key], ignore_index=True)
		else:
			data = dataDict[key]
		
		print '\n'
		print key
		
#		learn1Idx = data['oc'].values==1
#		learn2Idx = data['oc'].values==2
#		learn3Idx = data['oc'].values==3
#		test1Idx = testDataDict[key]['oc'].values==1
#		test2Idx = testDataDict[key]['oc'].values==2
#		test3Idx = testDataDict[key]['oc'].values==3

		self.plot_rawdata(testDataDict[key][key], testDataDict[key].drop(key,axis=1))

		print "------Linear Regression------"
		self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=LinearRegression(),filename='figs/'+key+'_linearRegress.pdf')
		print "------Linear SVM------"
		self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=LinearSVR(verbose=True),filename='figs/'+key+'_linearSVM.pdf')
		print "------RBF SVM------"
		self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=SVR(kernel='rbf', verbose=False), filename='figs/'+key+'_rbfSVM.pdf')
		#self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=SVR(kernel='sigmoid', verbose=True), filename='figs/'+key+'_sigmoidSVM.pdf')
		print " Newton Logistic"
#		self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=LogisticRegression(solver='newton-cg'), filename='figs/'+key+'_newtonLogistic.pdf')
		print " LBFGS Logistic"
		#self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=LogisticRegression(solver='lbfgs'), filename='figs/'+key+'_lbfgsLogistic.pdf')
		print " Liblinear Logistic"
		#self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=LogisticRegression(solver='liblinear'), filename='figs/'+key+'_liblinLogistic.pdf')
		print "Gaussian Naive Bayes"
		#self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=GaussianNB())
		#self.fit_data(data[key], data.drop(key,axis=1), testDataDict[key][key], testDataDict[key].drop(key,axis=1), model=MultinomialNB())
	
	def fit_data(self, y, xs, testy, testxs, model=SVR(kernel='rbf'),filename='figs/test.pdf'):
		#svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
		#svr_rbf = SVR()
		fitted = model.fit(xs,y)
		try:
			print xs.keys()
			print model.coef_
			pass
		except:
			pass
		y_rbf = fitted.predict(xs)
		#ax1 = fig.add_subplot(2,2,1,projection='3d')
		#ax1.scatter(xs[xs.keys()[0]],xs[xs.keys()[1]],y,c='k')
		
		#ax2 = fig.add_subplot(2,2,2,projection='3d')
		#ax2.scatter(xs[xs.keys()[0]],xs[xs.keys()[1]],y_rbf,c='k')

		testy_rbf = fitted.predict(testxs)
		#ax3 = fig.add_subplot(2,2,3,projection='3d')
		#ax3.scatter(testxs[testxs.keys()[0]],testxs[testxs.keys()[1]],testy,c='k')

		#ax4 = fig.add_subplot(2,2,4,projection='3d')
		#ax4.scatter(testxs[testxs.keys()[0]],testxs[testxs.keys()[1]],testy_rbf,c='k')
		testRmse = sqrt(mean_squared_error(testy, testy_rbf))
		learnRmse = sqrt(mean_squared_error(y, y_rbf))
		normRmse = testRmse/np.mean(testy)
		print 'Learn RMSE:\t', learnRmse
		print 'Test RMSE:\t', testRmse
		print '\n'

		#fig = plt.figure()
		#ax1 = fig.add_subplot(121)
		#ax1.plot(y,c='b')
		#ax1.plot(xs[xs.keys()[0]], c='r')
		#ax2 = fig.add_subplot(122)
		#ax2.plot(y, c='b')
		#ax2.plot(xs[xs.keys()[1]], c='r')
		#plt.show()


		fig = plt.figure()
		ax1 = fig.add_subplot(121)
		plotList = list()
		#plotList.append(ax1.plot_date(y.index, y, c='b', label='original', marker='None', linestyle='-'))
		#plotList.append(ax1.plot_date(y.index, y_rbf, c='r', label='fitted', marker='None', linestyle='-'))
		plotList.append(ax1.plot(y, c='b', label='original', marker='None', linestyle='-'))
		plotList.append(ax1.plot(y_rbf, c='r', label='fitted', marker='None', linestyle='-'))
		ax1.set_title('Learning Data')
		ax1.legend()
		plotList = list()
		ax2 = fig.add_subplot(122)
#		plotList.append(ax2.plot_date(testy.index, testy, c='b', label='original', marker='None', linestyle='-'))
#		plotList.append(ax2.plot_date(testy.index, testy_rbf, c='r', label='fitted', marker='None', linestyle='-'))
		plotList.append(ax2.plot(testy, c='b', label='original', marker='None', linestyle='-'))
		plotList.append(ax2.plot(testy_rbf, c='r', label='fitted', marker='None', linestyle='-'))
		ax2.set_title('Test Data')
		ax2.legend()
		plotter.save_fig(fig, filename)
		plt.show()
		
		pass
