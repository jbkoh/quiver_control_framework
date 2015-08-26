import master_actuator
from master_actuator import Actuator 
from bd_wrapper import bdWrapper
from actuator_names import ActuatorNames


#TODO: All the types of actuators classes should be implemented here with the super class, Actuator.


def make_actuator(self, zone, actuType):
	actuNames = ActuatorNames()
	if actuType==actuNames.commonSetpoint:
		return CommonSetpoint(66,74,zone)
	else:
		print "Failed to make an actuator: incorrect type name, " + actuType
		return None

class CommonSetpoint(Actuator):
	inputType = None
	zone = None
	bdm = None
	sensorType = 'PresentValue'
	template = None
	actuNames = ActuatorNames()

	def __init__ (self, minVal, maxVal, zone):
		inputType = master_actuator.TempType(self.minVal, self.maxVal)
		self.zone = zone
		self.bdm = bdWrapper()
		self.template = self.actuNames.commonSetpoint

	def set_value(self,ts)
# ts(list of dict) -> 
		for onedict in ts:
			if inputType.validate(self, onedict.values[0]):
			
		else:
			print "Failed to validate a value of " + zone + '\'s Common Setpoint to ' + str(givenVal)
		context = {'room':'rm-'+self.zone, 'template':self.template}
		uuid = self.bdm.get_sensor_uuids(context)[0]
		self.bdm.set_sensor_ts(uuid, self.sensorType, ts)

	def get_values(self, beginTime, endTime):
		pass

	def reset_value(self):
		pass
