class SensorNames:
	zoneTemperature = 'Zone Temperature'
	actualSupplyFlow = 'Actual Supply Flow'
	nameList = None
	
	def __init__(self):
		self.nameList = list()
		self.nameList.append(self.zoneTemperature)
		self.nameList.append(self.actualSupplyFlow)
	def __contains__(self, given):
		if given in self.nameList:
			return True
		else:
			return False

