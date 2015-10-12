import quiver_plot
reload(quiver_plot)
from quiver_plot import QuiverPlotter
import plotter
import sys

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt


timeFormat = '%Y-%m-%dT%H:%M:%S'
qp = QuiverPlotter()

def plot_all_change_one_zone(zone, beginTime, endTime):
	dataDict = list()
	dataDict.append((zone, ['Common Setpoint', 'Zone Temperature', 'Actual Cooling Setpoint', 'Actual Heating Setpoint'], 'Temperature'))
	dataDict.append((zone, 'Occupied Command', 'Status'))
	dataDict.append((zone, ['Cooling Command', 'Heating Command', 'Reheat Valve Command'], 'Command (%)'))
	dataDict.append((zone, ['Actual Supply Flow', 'Actual Sup Flow SP'], 'Air Flow ()'))
	dataDict.append((zone, ['Damper Command', 'Damper Position'], ['Command', 'Position (%)']))
	#qp.plot_multiple_rawdata(dataDict, datetime(2015,9,23,10),datetime(2015,9,23,18))
	qp.plot_multiple_rawdata(dataDict, beginTime, endTime, filename='sample_control.pdf', figSize=(4,8))

def plot_cmap_dep():
	filename = 'C:\Users\jbkoh\Documents\ipython\quiver_control_framework/result/dep_result.xlsx'
	data = pd.read_excel(filename)
	dataArray = data.fillna(0).as_matrix()
	xlabel = 'Prior Event'
	ylabel = 'Post Event'
	cbarLabel = 'P(Post Event|Prior Event)'
	cmap = cm.Blues
	xtickTags = ['Temperature Setpoint', 'Occupied Command', 'Cooling Command', 'Heating Command', 'Supply Air Flow Setpoint', 'Damper Command']
	xticks = range(0,5)
	
	fig, ax = plt.subplots(1,1)
	plotter.plot_colormap_upgrade2(dataArray, xlabel=xlabel, ylabel=ylabel, cbarLabel=cbarLabel, cmapIn=cmap, fig=fig, ax=ax)




plot_cmap_dep()
plot_all_change_one_zone('RM-4152', datetime(2015,10,7,19,30), datetime(2015,10,8,8,30))
