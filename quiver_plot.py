from bd_wrapper import BDWrapper
import plotter
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from pytz import timezone


class QuiverPlotter:
	bdm = None
	baseDir = 'figs/'
	pst = timezone("US/Pacific")

	def __init__(self):
		self.bdm = BDWrapper()
	
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
	def plot_multiple_rawdata(self, dataDict, beginTime, endTime):
		dataNum = len(dataDict)

		fig, axes = plt.subplots(dataNum,1)
#		g = lambda tp:tp.replace(tzinfo=None)	
		g = lambda tp:self.pst.localize(tp)
		for idx, (zone, actuType) in enumerate(dataDict):
			title = zone + ", " + actuType
			uuid = self.get_actuator_uuid(zone, actuType)
			data = self.bdm.get_sensor_ts(uuid, 'PresentValue', beginTime, endTime)
			tp = map(g, data.index)
			plotter.plot_timeseries(tp, data.values, axis=axes[idx], title=title)

		fig.set_size_inches((10,12))
		plotter.save_fig(fig, self.baseDir+"test.pdf")

		plt.show()

