import pickle
import pdb
from analyzer import Analyzer
import sys

with open('data/2015-09-28T1.pkl','rb') as fp:
#with open('data/2015-09-23T1.pkl','rb') as fp:
	dataDict = pickle.load(fp)

ztDict = dict()
for zone, value in dataDict.iteritems():
	ztDict[zone] = value['Zone Temperature']


anal = Analyzer()
if sys.argv[1]=='1':
	pdb.run("featDict = anal.clustering(dataDict['RM-4132']['Common Setpoint'], ztDict)")
else:
	featDict = anal.clustering(dataDict['RM-4132']['Common Setpoint'], ztDict)

print featDict
