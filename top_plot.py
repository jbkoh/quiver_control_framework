import quiver_plot
reload(quiver_plot)
from quiver_plot import QuiverPlotter

from datetime import datetime

qp = QuiverPlotter()
dataDict = list()
dataDict.append(('RM-4132', 'Actual Sup Flow SP'))
#dataDict.append(('RM-4132', 'Occupied Clg Min'))
dataDict.append(('RM-4132', 'Cooling Command'))
dataDict.append(('RM-4132', 'Occupied Command'))
dataDict.append(('RM-4132', ['Zone Temperature', 'Actual Cooling Setpoint', 'Actual Heating Setpoint']))
qp.plot_multiple_rawdata(dataDict, datetime(2015,9,23,10),datetime(2015,9,23,18))
