from bd_wrapper import BDWrapper
import plotter
reload(plotter)
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from pytz import timezone
from quiver import QRError
from analyzer import Analyzer
from matplotlib.dates import DateFormatter
from pytz import timezone

pst = timezone('US/Pacific')


class QuiverPlotter:
	bdm = None
	baseDir = 'figs/'
	pst = timezone("US/Pacific")
	anal = None

	def __init__(self):
		self.bdm = BDWrapper()
		self.anal = Analyzer()
	
	def get_actuator_uuid(self, zone=None, actuType=None):
		context = dict()
		if zone != None:
			context['room']=zone
		if actuType != None:
			context['template']=actuType
		uuids = self.bdm.get_sensor_uuids(context)
		if len(uuids)>1:
			raise QRError('Many uuids are found', context)
		elif len(uuids)==0:
			raise QRError('No uuid is found', context)
		else:
			return uuids[0]

#in dataDict, key: zone, value: actuType
	def plot_multiple_rawdata(self, dataDict, beginTime, endTime, filename='test.pdf', figSize=None):
		dataNum = len(dataDict)
		legendFontSize =7 
		clist= ['darkblue', 'darkseagreen', 'black']
		llist = ['-','-','-.']

		fig, axes = plt.subplots(dataNum,1,sharex=True)
		dataLabelIdx = 0
#		g = lambda tp:tp.replace(tzinfo=None)	
		g = lambda tp:self.pst.localize(tp)
		#dateFormat = None
		dateFormat = DateFormatter('%I %p', tz=pst)
		for idx, (zone, actuType, ylabels, yminmax, ytickRange, ytickTags) in enumerate(dataDict):
			if yminmax!=None:
				ymin=yminmax[0]
				ymax=yminmax[1]
			else:
				ymin=None
				ymax=None

			print zone, actuType, ylabels
			if idx !=len(dataDict)-1:
				xticks = []
				xtickTags = []
				xlabel = None
			else:
				xticks = None
				xtickTags = None
				xlabel = 'Time (Hour)'

			if type(actuType)!=list:
				#title = zone + ", " + actuType
				title = None
				if actuType=='Occupied Command':
					ymin = 0.7
					ymax = 3.3
					ytickRange = [1,2,3]
					ytickTags = ['Empty', 'Standby', 'Occupied']
					ytickRotate = 70
				else:
					ytickRotate = None
				uuid = self.get_actuator_uuid(zone, actuType)
#				data = self.bdm.get_sensor_ts(uuid, 'PresentValue', beginTime, endTime)
				data = self.anal.receive_a_sensor(zone, actuType, beginTime, endTime, 'nextval')
				tp = map(g, data.index)
				plotter.plot_timeseries(tp, data.values, axis=axes[idx], ylabel=ylabels, title=title, dataLabel=actuType, xticks=xticks, xtickTags=xtickTags, ymin=ymin, ymax=ymax, yticks=ytickRange, ytickTags=ytickTags, xlabel=xlabel, ytickRotate=ytickRotate, color=clist[0], lineStyle=llist[0])
				axes[idx].legend(loc='best', fontsize=legendFontSize)
			else:
				plotObjList = list()
				if len(actuType)==4:
					ncol=2
				else:
					ncol=2#
				bboxLoc = (0,1.05,1.,0.102)
				if 'Damper Position' in actuType:
					uuid1 = self.get_actuator_uuid(zone, actuType[0])
					uuid2 = self.get_actuator_uuid(zone, actuType[1])
					data1 = self.bdm.get_sensor_ts(uuid1, 'PresentValue', beginTime, endTime)
					data2 = self.bdm.get_sensor_ts(uuid2, 'PresentValue', beginTime, endTime)
					tp1 = map(g, data1.index)
					tp2 = map(g, data2.index)
					ax1 = axes[idx]
					ax2 = ax1.twinx()
					_,_,plotObj = plotter.plot_timeseries(tp1,data1.values, axis=ax1, ylabel=ylabels[0], dataLabel=actuType[0], xticks=xticks, xtickTags=xtickTags, dateFormat=dateFormat, color=clist[0], xlabel=xlabel, ymin=ymin, ymax=ymax, yticks=ytickRange[0], ytickTags=ytickTags[0])
					plotObjList.append(plotObj)
					_,_,plotObj = plotter.plot_timeseries(tp2,data2.values, axis=ax2, ylabel=ylabels[1], dataLabel=actuType[1], xticks=xticks, xtickTags=xtickTags, dateFormat=dateFormat, color=clist[1], xlabel=xlabel, ymin=ymin, ymax=ymax, yticks=ytickRange[1], ytickTags=ytickTags[1])
					plotObjList.append(plotObj)
					#axes[idx].legend(loc=3, bbox_to_anchor=bboxLoc, ncol=3, fontsize=legendFontSize, borderaxespad=0)
					axes[idx].legend(loc='best',fontsize=legendFontSize, borderaxespad=0)
					#ax2.legend(loc=3, bbox_to_anchor=bboxLoc, ncol=3, fontsize=legendFontSize,borderaxespad=0)
					ax2.legend(loc='best', fontsize=legendFontSize,borderaxespad=0)
				else:
					for innerIdx, oneActu in enumerate(actuType):
						uuid = self.get_actuator_uuid(zone, oneActu)
						data = self.bdm.get_sensor_ts(uuid, 'PresentValue', beginTime, endTime)
						tp = map(g, data.index)
#						if dataLabels!=None:
	#						dataLabel = dataLabels[dataLabelIdx]
#							dataLabelIdx += 1
#						else:
#							dataLabel = None
						_,_,plotObj = plotter.plot_timeseries(tp,data.values, axis=axes[idx], ylabel=ylabels, dataLabel=oneActu, xticks=xticks, xtickTags=xtickTags, xlabel=xlabel, color=clist[innerIdx], lineStyle=llist[innerIdx], yticks=ytickRange, ytickTags=ytickTags, ymin=ymin, ymax=ymax)
						plotObjList.append(plotObj)
					#axes[idx].legend(loc=3, bbox_to_anchor=bboxLoc, ncol=ncol,fontsize=legendFontSize, borderaxespad=0, mode='expand')
					axes[idx].legend(loc='best', ncol=ncol,fontsize=legendFontSize, borderaxespad=0, mode='expand')

		plt.subplots_adjust(hspace=0.1)	
		if figSize!=None:
			fig.set_size_inches(figSize)
		plotter.save_fig(fig, self.baseDir + filename)

		plt.show()

