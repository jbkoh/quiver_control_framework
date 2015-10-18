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
dataDict.append((zone, 'Occupied Command',None,None,None,None))
dataDict.append((zone, 'Reheat Valve Command',None,None,None,None))
#dataDict.append((zone, 'Actual Supply Flow'))
dataDict.append((zone, 'Damper Command',None,None,None,None))
#dataDict.append((zone, 'Damper Position',None,None,None,None))
dataDict.append((zone, 'Actual Sup Flow SP',None,None,None,None))
dataDict.append((zone, 'Cooling Command',None,None,None,None))
dataDict.append((zone, 'Heating Command',None,None,None,None))
dataDict.append((zone, ['Actual Cooling Setpoint', 'Actual Heating Setpoint', 'Zone Temperature'],None,None,None,None))
dataDict.append((zone, ['Actual Cooling Setpoint', 'Actual Heating Setpoint', 'Common Setpoint'],None,None,None,None))
#qp.plot_multiple_rawdata(dataDict, datetime(2015,9,23,10),datetime(2015,9,23,18))
qp.plot_multiple_rawdata(dataDict, beginTime, endTime)
