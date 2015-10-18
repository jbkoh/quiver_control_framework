import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import operator
import matplotlib
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math
from pytz import timezone

#class plotter:
# dataSeries (2-dimensional np.ndarray), figSize (tuple, length=2) -> fig
# each row of dataSeries is one data type.
# Other details should be implemented in inheritor

# NOTE
# Variable details:
# tickRanges: np.arange, contains tick numbers
# tickTags: list of tick name, contains tick names

pst = timezone("US/Pacific")


def save_fig(fig, name):
	pp = PdfPages(name)
	pp.savefig(fig, bbox_inches='tight', pad_inches=0, dpi=400)
	pp.close()


################################################### dataSeries (2-dimensional np.ndarray), figSize (tuple, length=2) -> fig
# dataSeries (list of np.ndarray), figSize (tuple, length=2) -> fig
# stackNum starts from 0, which means no stack but just a bar.
# each row of dataSeries is one data type.
# number of stackNum indicates the dats to be stacked.
# e.g., if length of dataSeries is 6, and stack Num is 2,
# dataSeries[0] and dataSereis[1] should be stacked on same bar
# dataSeries[1] and dataSereis[2] should be stacked on same bar
# dataSeries[3] and dataSereis[4] should be stacked on same bar
# Other details should be implemented in inheritor
def plot_multiple_stacked_bars(dataSeries, stackNum, xlabel=None, ylabel=None, xtickRange=None, xtickTag=None, ytickRange=None, ytickTag=None, title=None, stdSeries=None, axis=None, fig=None, clist=None, dataLabels=None, ylim=None, linewidth=0.2, xtickRotate=None, legendLoc='best', hatchSeries=None, eclist=None, oneBlockWidth=0.8):
	barNum = len(dataSeries)/(stackNum+1)
	totalBlockWidth = 0.8
	#oneBlockWidth = float(0.8/float(barNum))
	oneBlockWidth = float(oneBlockWidth/float(barNum))
	originalOneBlockWidth = float(0.8/float(barNum))
	x = np.arange(0,len(dataSeries[0]))
	if axis==None:
		#axis = plt.gca()
		fig, axis = plt.subplots(1,1)
	bars = list()
	colorIdx = 0
	dataLabelIdx = 0
	hatchLabelIdx = 0
	ecolorIdx = 0
	for barIdx in range(0,barNum):
		xpos = x-totalBlockWidth/2.0 + originalOneBlockWidth*barIdx + originalOneBlockWidth/2.0
		if clist:
			color = clist[colorIdx]
			colorIdx += 1
		else:
			color = None
		if dataLabels:
			dataLabel = dataLabels[dataLabelIdx]
			dataLabelIdx += 1
		else:
			dataLabel = None
		if hatchSeries != None:
			hatch = hatchSeries[hatchLabelIdx]
			hatchLabelIdx += 1
		else:
			hatch=None
		if eclist != None:
			ecolor = eclist[ecolorIdx]
			ecolorIdx +=1 
		else:
			ecolor = None
		#bars.append(axis.bar(xpos, dataSeries[barIdx*(stackNum+1)], yerr=std, width = oneBlockWidth, align='center', color=color, label=dataLabel, linewidth=linewidth, hatch=hatch, ecolor=ecolor))
		bars.append(axis.bar(xpos, dataSeries[barIdx*(stackNum+1)], width = oneBlockWidth, align='center', color=color, label=dataLabel, linewidth=linewidth, hatch=hatch))
		if stdSeries:
			std = stdSeries[barIdx*(stackNum+1)]
			axis.errorbar(xpos, dataSeries[barIdx*(stackNum+1)], yerr=std, ecolor=ecolor,elinewidth=0.3, capthick=0.3, fmt=None, capsize=2)
		offset = dataSeries[barIdx]
		for stackIdx in range(1,stackNum+1):
			if stdSeries:
				std = stdSeries[barIdx*(stackNum+1)]
			else:
				std = None
			if clist:
				color = clist[colorIdx]
				colorIdx += 1 
			else:
				color = None
			if dataLabels:
				dataLabel = dataLabels[dataLabelIdx]
				dataLabelIdx += 1
			else:
				dataLabel = None
			if hatchSeries != None:
				hatch = hatchSeries[hatchLabelIdx]
				hatchLabelIdx += 1
			else:
				hatch=None
			if eclist != None:
				ecolor = eclist[ecolorIdx]
				ecolorIdx +=1 
			else:
				ecolor = None
			bars.append(axis.bar(xpos, dataSeries[barIdx*(stackNum+1)+stackIdx], yerr=std, width=oneBlockWidth, bottom=offset, align='center', color=color, label=dataLabel, linewidth=linewidth, hatch=hatch, ecolor=ecolor))
			#plt.bar(xpos, dataSeries[barIdx*stackNum+stackIdx], yerr=std, width=oneBlockWidth, bottom=offset, align='center')
			offset += dataSeries[barIdx*(stackNum+1)+stackIdx]
	
	#plt.xlim(x[0]-1,x[len(x)-1]+1)
	axis.set_xlim(x[0]-1,x[len(x)-1]+1)
	if ylim:
		axis.set_ylim(ylim)
	if ylabel:
		axis.set_ylabel(ylabel, labelpad=-0.5)
#		axis.set_ylabel(ylabel)
	if xlabel:
	#	plt.xlabel(xlabel, labelpad=-2)
		axis.set_xlabel(xlabel, labelpad=-0.5)
#		axis.set_xlabel(xlabel)
	
	if dataLabels: 
		axis.legend(handles=bars, fontsize=8, loc=legendLoc)
	if xtickTag != None:
		if not xtickRange:
			xtickRange = np.arange(0,len(dataSeries[0])+1, math.floor(float(len(dataSeries[0])/(len(xtickTag)-1))))
			#xtickRange = np.arange(0,len(xtickTag))
		if xtickRotate == None:
			xtickRotate = 70
		#plt.xticks(xtickRange, xtickTag, fontsize=10, rotation=70)
		axis.set_xticks(xtickRange)
		axis.set_xticklabels(xtickTag, fontsize=8, rotation=xtickRotate)
	if ytickTag != None:
		if ytickRange==None:
			ytickRange = np.arange(0,len(ytickTag))
		#plt.yticks(ytickRange, ytickTag, fontsize=10)
		axis.set_yticks(ytickRange)
		axis.set_yticklabels(ytickTag, fontsize=8)
	if title:
		#plt.title(title)
		axis.set_title(title, y=1.08)
	return fig, bars

def plot_up_down_bars(upData, downData, upStd=None, downStd=None, xlabel=None, ylabel=None, title=None, axis=None, fig=None, upColor=None, downColor=None, dataLabels=None, legendLoc='best'):
	if fig==None and axis==None:
		fig, axis = plt.subplots(1,1)
	barNum = len(upData)
	if barNum != len(downData):
		print "data length mismatch"
		return None
	blockWidth = 0.5
	x = np.arange(0,barNum)
	bars = list()
	if dataLabels != None:
		legendUp = dataLabels[0]
		legendDown = dataLabels[1]
	bars.append(axis.bar(x,upData, yerr=upStd, color=upColor, align='center', label=legendUp))
	bars.append(axis.bar(x,downData, yerr=downStd, color=downColor, align='center', label=legendDown))
	if dataLabels != None:
		axis.legend(handles=bars, fontsize=8, loc=legendLoc)
	axis.set_ylabel(ylabel, labelpad=-2)
	axis.set_xlabel(xlabel, labelpad=-2)
	axis.set_xlim(x[0]-1,x[len(x)-1]+1)
	if title:
		plt.title(title)
	return fig

def plot_colormap(data, figSizeIn, xlabel, ylabel, cbarlabel, cmapIn, ytickRange, ytickTag, xtickRange=None, xtickTag=None, title=None):
	fig = plt.figure(figsize = figSizeIn)
	plt.pcolor(data, cmap=cmapIn)
	cbar = plt.colorbar()
	cbar.set_label(cbarlabel, labelpad=-0.1)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	if xtickTag:
		plt.xticks(xtickRange, xtickTag, fontsize=10)

	plt.yticks(ytickRange, ytickTag, fontsize=10)
	plt.tight_layout()
	if title:
		plt.title(title)
	plt.show()
	return fig

def plot_colormap_upgrade2(data, xlabel=None, ylabel=None, cbarLabel=None, cmapIn=None, ytickRange=None, ytickTags=None, xtickRange=None, xtickTags=None, title=None, xmin=None, xmax=None, xgran=None, ymin=None, ymax=None, figSizeIn=None, ygran=None, fig=None, ax=None, cbarTicks=None, cbartickLabels=None, xtickRotate=0):
	if fig==None:
		fig, ax = plt.subplots(1,1)
	if xmin != None:
		y, x = np.mgrid[slice(ymin, ymax + ygran, ygran),
				slice(xmin, xmax + xgran, xgran)]
#		plt.pcolor(data, cmap=cmapIn)
		p = ax.pcolormesh(x, y, data, cmap=cmapIn)
		ax.grid(which='major',axis='both')
		ax.set_axes([x.min()-1, x.max()+1, y.min(), y.max()])
	else:
		p = ax.pcolormesh(data, cmap=cmapIn)

	if cbarTicks!=None:
		cbar = fig.colorbar(p, ticks=cbarTicks)
		cbar.ax.set_yticklabels(cbartickLabels)
	else:
		cbar = fig.colorbar(p)
	cbar.set_label(cbarLabel, labelpad=1)
	if xlabel!=None:
		ax.set_xlabel(xlabel)

	if ylabel!=None:
		ax.set_ylabel(ylabel)
	if xtickTags!=None and xtickRange!=None:
		ax.set_xticks(xtickRange)
		ax.set_xticklabels(xtickTags, fontsize=9, horizontalalignment='left', rotation=xtickRotate)
		#ax.tick_params(left='on', right='on')
#		for label in ax.xaxis.get_majorticklabels():
#			label.set_position((1,1))
#		label = ax.xaxis.get_majorticklabels()[3]
#		print label.get_position()
#		label.set_position((5,1))
#		print label.get_position()

		#ax.tick_params(direction='right', pad=20)

	if ytickTags!=None and ytickRange!=None:
		ax.set_yticks(ytickRange)
		ax.set_yticklabels(ytickTags, fontsize=9, verticalalignment='bottom')

#	if xmin!=None and xmax!= None:
#		ax.set_xlim((xmin, xmax))
#	if ymin!=None and ymax!=None:
#		ax.set_ylim((ymin-1, ymax+1))
	if title:
		ax.set_title(title)
	plt.tight_layout()
#	plt.show()
	return fig, ax


def plot_colormap_upgrade(data, figSizeIn, xlabel, ylabel, cbarlabel, cmapIn, ytickRange, ytickTag, xtickRange=None, xtickTag=None, title=None, xmin=None, xmax=None, xgran=None, ymin=None, ymax=None, ygran=None):
	fig = plt.figure(figsize = figSizeIn)
	if xmin != None:
		y, x = np.mgrid[slice(ymin, ymax + ygran, ygran),
				slice(xmin, xmax + xgran, xgran)]
#		plt.pcolor(data, cmap=cmapIn)
		plt.pcolormesh(x, y, data, cmap=cmapIn)
		plt.grid(which='major',axis='both')
		plt.axis([x.min()-1, x.max()+1, y.min(), y.max()])
	else:
		plt.pcolor(data, cmap=cmapIn)

	cbar = plt.colorbar()
	cbar.set_label(cbarlabel, labelpad=-0.1)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
#	if xtickTag:
#		plt.xticks(xtickRange, xtickTag, fontsize=10)
#
#	plt.yticks(ytickRange, ytickTag, fontsize=10)
	plt.tight_layout()
	if xmin!=None and xmax!= None:
		plt.xlim((xmin-1, xmax+1))
	if ymin!=None and ymax!=None:
		plt.ylim((ymin-1, ymax+1))
	if title:
		plt.title(title)
	plt.show()
	return fig

def plot_timeseries(x, y, xlabel=None, ylabel=None,  xticks=None, xtickTags=None, yticks=None, ytickTags=None, title=None, xtickRotate=None, dateFormat=None,color=None, axis=None, fig=None, dataLabel=None, ymin=None, ymax=None, xmax=None, xmin=None, ytickRotate=None, lineStyle='-'):
	if axis==None:
		fig, axis = plt.subplots(1,1)
	
	plotObj = axis.plot_date(x, y, linestyle=lineStyle, marker='None',tz=pst, color=color, label=dataLabel)
	if xmin!=None and xmax!= None:
		axis.set_xlim((xmin-1, xmax+1))
	if ymin!=None and ymax!=None:
		axis.set_ylim((ymin, ymax))

	xtickFontSize = 7
	ytickFontSize = 7
	ylabelFontSize = 7

	if xlabel!=None:
		axis.set_xlabel
	if ylabel!=None:
		axis.set_ylabel(ylabel, fontsize=ylabelFontSize)
	if xticks:
		axis.set_xticks(xticks)
	if xtickTags:
		axis.set_xticklabels(xtickTags)
	if yticks != None:
		axis.set_yticks(yticks)
	if ytickTags!=None:
		ytickLabel = ytickTags
	else:
		ytickLabel = axis.get_yticks().tolist()
	if title:
		axis.set_title(title)
	if xtickRotate != None:
		xtickLabel = axis.get_xticklabels()
		axis.set_xticklabels(xtickLabel, rotation=xtickRotate, fontsize=xtickFontSize)
	else:
		xtickLabel = axis.get_xticklabels()
		axis.set_xticklabels(xtickLabel, fontsize=xtickFontSize)
#	ytickLabel = [item.get_text() for item in axis.get_yticklabels()]
	axis.set_yticklabels(ytickLabel, fontsize=ytickFontSize,rotation=ytickRotate)
	
	#fig.autofmt_xdate()
	if dateFormat!=None:
		axis.xaxis.set_major_formatter(dateFormat)
	
	if title!=None:
		axis.set_title(title)
		
	
	return fig, axis, plotObj

# x (list of np.array(datetime)), y (list of np.array(number)) -> fig 
def plot_multiple_timeseries(xs, ys, xlabel, ylabel, xticks=None, xtickTags=None, yticks=None, ytickTags=None, titles=None, xtickRotate=None, dateFormat=None,color=None):
	dataNum = len(ys)
	fig, axes = plt.subplots(dataNum)
	for i, axis in enumerate(axes):
		#plt.xticks(rotation='70')
		axis.plot_date(xs[i], ys[i], linestyle='-', marker='None',tz=pst, color=color)
		axis.set_xlabel(xlabel)
		axis.set_ylabel(ylabel)
#		axis.set_ylim([0.9,3.1])
		if xticks:
			axis.set_xticks(xticks[i])
		if xtickTags:
			axis.set_xticklabels(xtickTags[i])
		if yticks:
			axis.set_yticks(yticks[i])
		if ytickTags:
			axis.set_yticklabels(ytickTags[i])
		if titles:
			axis.set_title(titles[i])
		if xtickRotate != None:
			xtickLabel = axis.get_xticklabels()
			axis.set_xticklabels(xtickLabel, rotation=xtickRotate, fontsize=8)
		#fig.autofmt_xdate()
		if dateFormat!=None:
			axis.xaxis.set_major_formatter(dateFormat)


	fig.subplots_adjust(hspace=0.4)
	#fig.autofmt_xdate()
	return fig, axes

def plot_multiple_2dline(x, ys, xlabel=None, ylabel=None, xtick=None, xtickLabel = None, ytick=None, ytickLabel=None, title=None, axis=None, fig=None, ylim=None, dataLabels=None):
	dataNum = len(ys)
	if axis==None and fig==None:
		fig, axis = plt.subplots(1,1)
	dataLabelIdx = 0
	plotList = list()
	for i in range(0,dataNum):
		if dataLabels:
			dataLabel = dataLabels[dataLabelIdx]
			dataLabelIdx += 1
		else:
			dataLabel = None
		axis.plot(x,ys[i], label=dataLabel)
	if dataLabels:
		axis.legend(fontsize=7, loc='best')
	if ylim:
		axis.set_ylim(ylim)
	if xlabel:
		axis.set_xlabel(xlabel)
	if ylabel:
		axis.set_ylabel(ylabel)
	if xtick:
		axis.set_xticks(xtick)
	if xtickLabel:
		axis.set_xticklabels(xtickLabel)
	if ytick:
		axis.set_yticks(ytick)
	if ytickLabel:
		axis.set_yticklabels(ytickLabel)
	if title:
		axis.set_title(title)
#	if dataLabels: 
#		plt.legend(handles=plotList, fontsize=7)

	plt.show()
	return fig

def plot_yy_bar(dataSeries, xlabel=None, ylabel=None, xtickRange=None, xtickTag=None, ytickRange=None, ytickTag=None, title=None, stdSeries=None, axis=None, fig=None, clist=None, dataLabels=None, yerrs=None, ylim=None, linewidth=None):
	pass
	
def make_month_tag(baseTime):
	monthTags = list()
#	for i in range(0,21):
	while baseTime<datetime(2015,6,25):
		monthTags.append(baseTime.strftime('%b-\'%y'))
		baseTime += timedelta(days=31)

	return monthTags
