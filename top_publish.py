import quiver_plot
reload(quiver_plot)
from quiver_plot import QuiverPlotter
import plotter
import sys

import pdb
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt


timeFormat = '%Y-%m-%dT%H:%M:%S'
qp = QuiverPlotter()

def plot_all_change_one_zone(zone, beginTime, endTime):
	dataDict = list()
	ytickRange = [62,66,70,74,78]
	ytickTags = ['62','68','72','76','80']
	yminmax=((62,80))
	dataDict.append((zone, 'Common Setpoint', 'Temperature', yminmax, ytickRange, ytickTags))
	ytickRange = [60,65,70,75,80]
	ytickTags = ['60', '65', '70', '75', '80']
	yminmax=((60,85))
	dataDict.append((zone, ['Actual Cooling Setpoint', 'Actual Heating Setpoint', 'Zone Temperature'], 'Temperature',yminmax, ytickRange, ytickTags))
	ytickRange = [0,25,50,75,100]
	ytickTags = ['0', '25', '50', '75', '100']
	yminmax=((0,150))
	dataDict.append((zone, ['Cooling Command', 'Heating Command', 'Reheat Valve Command'], 'Command (%)', yminmax, ytickRange, ytickTags))
	ytickRange = [200,400,600,800]
	ytickTags = ['200', '400', '600', '800']
	yminmax=((200,900))
	dataDict.append((zone, ['Actual Supply Flow', 'Actual Sup Flow SP'], 'Air Flow ()', yminmax, ytickRange, ytickTags))
	ytickRange1 = [-0.2,0,0.2,0.4, 0.6]
	ytickTags1 = ['-0.2','0','0.2','0.4', '0.6']
	yminmax1=((-0.2,0.8))
	ytickRange2 = [30, 40, 50, 60, 70]
	ytickTags2 = ['30', '40', '50', '60', '70']
	yminmax2=((30,80))
	dataDict.append((zone, ['Damper Command', 'Damper Position'], ['Command', 'Position (%)'], [yminmax1,yminmax2], [ytickRange1,ytickRange2], [ytickTags1, ytickTags2]))
	#qp.plot_multiple_rawdata(dataDict, datetime(2015,9,23,10),datetime(2015,9,23,18))
	qp.plot_multiple_rawdata(dataDict, beginTime, endTime, filename='sample_control.pdf', figSize=(4,8))

def plot_cmap_dep():
	filename = 'result/dep_result_for_graph.xlsx'
	data = pd.read_excel(filename)
	dataArray = data.fillna(0).as_matrix()
	xlabel = 'Controlled Points'
	ylabel = 'Points'
	cbarLabel = 'P(#Dependent Change|\n #Controlled Change)'
	cmap = cm.Blues
	#xtickTags = ['Temperature Setpoint', 'Occupied Command', 'Cooling Command', 'Heating Command', 'Supply Air Flow Setpoint', 'Damper Command']
	xtickTags = ['TS', 'OC', 'CC', 'HC', 'RVC', 'SAFS', 'DC']
	ytickTags = ['TS', 'OC', 'CC', 'HC', 'RVC', 'SAFS', 'DC']
#	xtickRange = np.arange(0.5,6.5,1)
	xtickRange = range(0,7)
	#visibleXtickRange = range(0,6)
	#ytickRange = np.arange(0.5,7.5,1)
	ytickRange = range(0,7)
	cbarTicks = [0,0.25,0.5,0.75,1]
	cbartickLabels = ['0','0.25','0.5','0.75','1']

	xmin = 0
	ymin = 0
	xmax = 7
	ymax = 7
	
	fig, ax = plt.subplots(1,1)
	plotter.plot_colormap_upgrade2(dataArray, xlabel=xlabel, ylabel=ylabel, cbarLabel=cbarLabel, cmapIn=cmap, fig=fig, ax=ax, ytickTags=ytickTags, xtickRange=xtickRange, xtickTags=xtickTags, ytickRange=ytickRange, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,ygran=1,xgran=1, cbartickLabels=cbartickLabels, cbarTicks=cbarTicks)
	#ax.set_xticks(visibleXtickRange)
	fig.set_size_inches((4,2))
	plotter.save_fig(fig,'figs/dep_colormap.pdf')
	plt.show()

def plot_cmap_type():
	filename = 'result/type_id_result_for_graph.xlsx'
	data = pd.read_excel(filename)
	ytickTags = data['classifier'].tolist()
	data = data.drop('classifier',axis=1)
	dataArray = data.fillna(0).as_matrix()
	xlabel = 'Classifier (Features)'
	ylabel = 'Point Type'
	cbarLabel = 'Accruacy (%)'
	cmap = cm.Blues
	xtickTags = data.keys().to_series().map(str).tolist()
	#xtickTags = data.keys().to_series().tolist()
#	ytickTags = None
#	xtickRange = np.arange(0.5,6.5,1)
	xtickRange = range(0,13)
	#visibleXtickRange = range(0,6)
	#ytickRange = np.arange(0.5,7.5,1)
	ytickRange = range(0,16)
	xmin = 0
	ymin = 0
	xmax = 12
	ymax = 16
	xtickRotate=-60
	
	fig, ax = plt.subplots(1,1)
	plotter.plot_colormap_upgrade2(dataArray, xlabel=xlabel, ylabel=ylabel, cbarLabel=cbarLabel, cmapIn=cmap, fig=fig, ax=ax, ytickTags=ytickTags, xtickRange=xtickRange, xtickTags=xtickTags, ytickRange=ytickRange, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,ygran=1,xgran=1,xtickRotate=xtickRotate)
	#ax.set_xticks(visibleXtickRange)
	fig.set_size_inches((8,4))
	plotter.save_fig(fig,'figs/typeclass_colormap.pdf')
	plt.show()


plot_cmap_dep()
plot_cmap_type()
plot_all_change_one_zone('RM-1124', datetime(2015,10,12,20,50), datetime(2015,10,13,1))
#plot_all_change_one_zone('RM-4152', datetime(2015,10,7,19,30), datetime(2015,10,8,8,30))
