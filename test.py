import pickle
from analyzer import Analyzer

with open('data/2015-09-23T1.pkl','rb') as fp:
	dataDict = pickle.load(fp)

ztDict = dict()
for zone, value in dataDict.iteritems():
	ztDict[zone] = value['Zone Temperature']


anal = Analyzer()
featDict = anal.clustering(dataDict['RM-4132']['Common Setpoint'], ztDict)
print featDict
