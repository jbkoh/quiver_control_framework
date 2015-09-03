class ActuatorNames:
	commonSetpoint = 'Common Setpoint'
	occupiedCommand = 'Occupied Command'
	nameList = list()
	
	def __init__(self):
		self.nameList.append(self.commonSetpoint)

	def __contains__(self, given):
		if given in self.nameList:
			return True
		else:
			return False

