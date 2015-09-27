
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from scipy.fftpack import fft
import dtw
import csv



class FeatureExtractor():
	zonelist = None
	datadir = 'data/'

	def __init__(self):
		self.zonelist = self.csv2list('metadata/partialzonelist.csv')
	
	def csv2list(self, filename):
		outputList = list()
		with open(filename, 'r') as fp:
			reader = csv.reader(fp, delimiter=',')
			for row in reader:
				outputList.append(row[0])
		return outputList

	def get_features(self, dataDict, featureType):
		if featureType=='fft':
			return self.get_fft_features(dataDict)
		else:
			return None
	
	def normalize(self, data):
		minVal = min(data)
		minmax = max(data)-min(data)
		data = (data-minVal)/minmax
		return data
	
	def get_fft_features(self, inputData, dataDict):
		fftDict = dict()
		distDict = dict()
		for zone, data in dataDict.iteritems():
			fftDict[zone] = np.fft.rfft(self.normalize(data))[:10]
		inputfft = np.fft.rfft(self.normalize(inputData))[:10]
		for zone, data in fftDict.iteritems():
			distDict[zone] = np.linalg.norm(fftDict[zone][1:]-inputfft[1:])
#			distDict[zone] = dtw.dtw(fftDict[zone][1:],inputfft[1:])
#			print zone, distDict[zone][0]
		return distDict

	def get_minmax_features(self, dataDict):
		minmaxDict = dict()
		for zone, data in dataDict.iteritems():
			minmaxDict[zone] = max(data)-min(data)
		return minmaxDict

	def get_dtw_features(self, inputData, dataDict):
		dtwDict = dict()
		for zone, data in dataDict.iteritems():
			dtwDict[zone] = dtw.dtw(inputData, data)[0]
		return dtwDict

	def get_freq(self, data):
		minmax = max(data) - min(data)
		beforeVal= data[0]
		afterVal = data[0]
		freq = 0
		val1 = data[0]
		val2 = data[0]
		ascendFlag = data[1]>=data[0]
		for datum in data:
			val2 = datum
			if val2==val1:
				ascendFlag = ascendFlag
			else:
				ascendFlag = val2>val1
			if beforeVal>datum and ascendFlag:
				beforeVal = datum
			elif beforeVal<datum and not ascendFlag:
				beforeVal = datum
			if afterVal<datum and ascendFlag:
				afterVal = datum
			elif afterVal>datum and ascendFlag:
				afterVal = datum

			if afterVal>=beforeVal+minmax/2 and ascendFlag:
				freq += 0.5
				ascendFlag = not ascendFlag
			elif afterVal<=beforeVal+minmax/2 and not ascendFlag:
				freq += 0.5
				ascendFlag = not ascendFlag
			va1 = datum
			
		return freq
	
	def get_freq_features(self, inputData, dataDict):
		freqDict = dict()
		targetFreq = self.get_freq(inputData)
		for zone, data in dataDict.iteritems():
			freqDict[zone] = self.get_freq(data) - targetFreq
		return freqDict

			

