
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
	
	def get_fft_features(self, inputData, dataDict):
		fftDict = dict()
		distDict = dict()
		for zone, data in dataDict.iteritems():
			fftDict[zone] = np.fft.rfft(data)
		inputfft = np.fft.rfft(inputData)
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


