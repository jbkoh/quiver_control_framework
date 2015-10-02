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
dataDict.append((zone, 'Actual Sup Flow SP'))
#dataDict.append((zone, 'Occupied Clg Min'))
dataDict.append((zone, 'Cooling Command'))
dataDict.append((zone, 'Occupied Command'))
dataDict.append((zone, ['Zone Temperature', 'Actual Cooling Setpoint', 'Actual Heating Setpoint']))
dataDict.append((zone, ['Common Setpoint', 'Actual Cooling Setpoint', 'Actual Heating Setpoint']))
#qp.plot_multiple_rawdata(dataDict, datetime(2015,9,23,10),datetime(2015,9,23,18))
qp.plot_multiple_rawdata(dataDict, beginTime, endTime)
