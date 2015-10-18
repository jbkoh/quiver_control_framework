import quiver_plot
reload(quiver_plot)
from quiver_plot import QuiverPlotter
import sys

from datetime import datetime

zoneList = ['RM-1150', 'RM-1218', 'RM-2150', 'RM-2232', 'RM-3132', 'RM-4106', 'RM-4126', 'RM-4134']
beginTimeStr = '2015-10-11T22:40:00'
endTimeStr = '2015-10-12T06:00:00'

timeFormat = '%Y-%m-%dT%H:%M:%S'
beginTime = datetime.strptime(beginTimeStr, timeFormat)
endTime = datetime.strptime(endTimeStr, timeFormat)
qp = QuiverPlotter()

for zone in zoneList:
	dataDict = list()
	#dataDict.append((zone, 'Common Setpoint'))
	#dataDict.append((zone, 'Warm Cool Adjust'))
	#dataDict.append((zone, 'Actual Cooling Setpoint'))
	#dataDict.append((zone, 'Temp Occ Sts'))
	dataDict.append((zone, 'Occupied Command',None))
	#dataDict.append((zone, 'Reheat Valve Command',None))
	#dataDict.append((zone, 'Actual Supply Flow'))
	dataDict.append((zone, 'Damper Command',None))
	#dataDict.append((zone, 'Damper Position'))
	dataDict.append((zone, 'Actual Sup Flow SP',None))
	dataDict.append((zone, 'Cooling Command',None))
	dataDict.append((zone, 'Heating Command',None))
	dataDict.append((zone, ['Zone Temperature', 'Actual Cooling Setpoint', 'Actual Heating Setpoint'],None))
	dataDict.append((zone, ['Common Setpoint', 'Actual Cooling Setpoint', 'Actual Heating Setpoint'],None))
	#qp.plot_multiple_rawdata(dataDict, datetime(2015,9,23,10),datetime(2015,9,23,18))
	qp.plot_multiple_rawdata(dataDict, beginTime, endTime)
