import master_actuator
from master_actuator import Actuator 
from bd_wrapper import bdWrapper
from actuator_names import ActuatorNames

from datetime import datetime, timedelta


#TODO: All the types of actuators classes should be implemented here with the super class, Actuator.


def make_actuator(zone, actuType):
	actuNames = ActuatorNames()
	if actuType==actuNames.commonSetpoint:
		return CommonSetpoint(66,74,zone)
	else:
		print "Failed to make an actuator: incorrect type name, " + actuType
		return None

class CommonSetpoint(Actuator):
	zone = None
	bdm = None
	sensorType = 'PresentValue'
	template = None
	actuNames = ActuatorNames()

	def __init__ (self, minVal, maxVal, zone):
		super(CommonSetpoint, self).__init__(timedelta(minutes=30))
		self.inputType = master_actuator.TempType(minVal, maxVal)
		self.zone = zone
		self.bdm = bdWrapper()
		self.template = self.actuNames.commonSetpoint

	def set_value(self, tp, val):
		super(CommonSetpoint, self).set_value(tp, val)
# ts(list of dict) -> 
		if inputType.validate(self, val):
			context = {'room':self.zone, 'template':self.template}
			uuid = self.bdm.get_sensor_uuids(context)[0]
			self.bdm.set_sensor(uuid, self.sensorType, tp, val)
		else:
			print "Failed to validate a value of " + zone + '\'s Common Setpoint to ' + str(givenVal)

	def get_value(self, beginTime, endTime):
		print "TODO: Implement Get Value"
		pass

	def reset_value(self):
		super(CommonSetpoint, self).reset_value()
		print "TODO: Implement Reset Value"
		pass
	
	#TODO: Do I need this?
	def set_reset_value(self):
		pass
		

	def check_dependency(self, actuType):
# actuType(str) -> dependent?(boolean)
		if actuType in self.dependentList:
			return True
		else:
			return False
