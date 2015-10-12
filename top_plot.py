import quiver_plot
reload(quiver_plot)
from quiver_plot import QuiverPlotter
import sys

from datetime import datetime

zone = sys.argv[1]
timeFormat = '%Y-%m-%dT%H:%M:%S'
beginTime = datetime.strptime(sys.argv[2], timeFormat)
endTime = datetime.strptime(sys.argv[3], timeFormat)
qp = QuiverPlotter()
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
