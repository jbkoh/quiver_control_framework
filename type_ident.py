import pickle
import pdb
from analyzer import Analyzer
import re
from sensor_names import SensorNames
from actuator_names import ActuatorNames
import sys

from datetime import datetime

sensorList = SensorNames().nameList
actuList = ActuatorNames().nameList

anal = Analyzer()
beginTime = datetime(2014,6,1)
endTime = datetime(2015,6,1)
knownzone = 'RM-1108'
#testzone = ['RM-1124', 'RM-4114', 'RM-2130', 'RM-3102', 'RM-4136', 'RM-4122', 'RM-4220', 'RM-2121', 'RM-1109', 'RM-1134', 'RM-3106']
testzone = ['RM-1109', 'RM-1124', 'RM-1134', 'RM-1144', 'RM-2130', 'RM-2121', 'RM-3102', 'RM-3106', 'RM-3110', 'RM-3130', 'RM-4114', 'RM-4220']

# Receive raw data for finding TS characteristics
#dataDict = dict()
#for pointType in sensorList+actuList:
#	try:
#		dataDict[pointType] = anal.receive_a_sensor(zone, pointType, beginTime, endTime, 'nextval')
#	except:
#		pass
#with open('data/oneyear_1108_0601.pkl', 'wb') as fp:
#	pickle.dump(dataDict, fp)
anal.store_zone_sensors(knownzone, beginTime, endTime, 'nextval', 'data\oneyear_1108_0601.pkl')
#anal.receive_entire_sensors(datetime(2015,8,1), datetime(2015,9,1), 'data/onemonth_allzones_0801.pkl', 'nextval')

for zone in testzone:
	anal.store_zone_sensors(zone, beginTime, endTime, 'nextval', 'data\oneyear_'+ re.search('\d+',zone).group() +'_0601.pkl')

# Receive controlled data for extracting features.
