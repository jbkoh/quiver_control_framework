class ActuatorNames:
	commonSetpoint = 'Common Setpoint'
	occupiedCommand = 'Occupied Command'
	coolingCommand = 'Cooling Command'
	actualSupplyFlowSP = 'Actual Sup Flow SP'
	heatingCommand = 'Heating Command'
	damperCommand = 'Damper Command'
	nameList = list()
	
	def __init__(self):
		self.nameList.append(self.commonSetpoint)

	def __contains__(self, given):
		if given in self.nameList:
			return True
		else:
			return False

