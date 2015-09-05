import master_actuator
from master_actuator import Actuator 
from actuator_names import ActuatorNames

from datetime import datetime, timedelta


#TODO: All the types of actuators classes should be implemented here with the super class, Actuator.


def make_actuator(uuid, name, zone=None, actuType=None):
	actuNames = ActuatorNames()
	if actuType==actuNames.commonSetpoint:
		return CommonSetpoint(name, uuid, 66,74,zone)
	else:
		print "Failed to make an actuator: incorrect type name, " + actuType
		return None

class CommonSetpoint(Actuator):
	zone = None
	sensorType = 'PresentValue'
	template = None
	actuNames = ActuatorNames()

#TODO: Is it okay to set minVal and maxVal arbitrarily outside this class?
	def __init__ (self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(CommonSetpoint, self).__init__(timedelta(minutes=1))
		self.inputType = master_actuator.TempType(minVal, maxVal)
		self.zone = zone
		self.template = self.actuNames.commonSetpoint

	def set_value(self, val, tp): # This is dummy for test
		super(CommonSetpoint, self).set_value(tp, val)
		if self.inputType.validate(val):
			pass
		else:
			print "Failed to validate a value of " + self.zone + '\'s Common Setpoint to ' + str(val)

	def reset_value(self,val,tp): # This is dummy for test
		super(CommonSetpoint, self).reset_value()

	def set_value_active(self, val, tp):
		super(CommonSetpoint, self).set_value(tp, val)
# ts(list of dict) -> 
		if self.inputType.validate(val):
			context = {'room':self.zone, 'template':self.template}
			uuid = self.bdm.get_sensor_uuids(context)[0]
			self.bdm.set_sensor(uuid, self.sensorType, tp, val)
		else:
			print "Failed to validate a value of " + zone + '\'s Common Setpoint to ' + str(givenVal)

	def get_value(self, beginTime, endTime):
#		return self.bdm.get_zone_sensor_ts(self.zone, self.template, self.sensorType, beginTime, endTime)
		return self.bdm.get_sensor_ts(self.uuid, self.sensorType, beginTime, endTime)

	def reset_value_active(self, val, tp):
		super(CommonSetpoint, self).reset_value()
		context = {'room':self.zone, 'template':self.template}
		uuid = self.bdm.get_sensor_uuids(context)[0]
		self.bdm.set_sensor(uuid, self.sensorType, tp, val)
	
	#TODO: Do I need this?
	def set_reset_value(self):
		pass

class ActualCoolingSetpoint(Actuator):
	zone = None
	sensorType = 'PresentValue'
	template = None
	actuNames = ActuatorNames()

#TODO: Is it okay to set minVal and maxVal arbitrarily outside this class?
	def __init__ (self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(ActualCoolingSetpoint, self).__init__(timedelta(minutes=2))
		self.inputType = master_actuator.TempType(minVal, maxVal)
		self.zone = zone
		self.template = self.actuNames.actualCoolingSetpoint

	def set_value(self, val, tp): # This is dummy for test
		super(ActualCoolingSetpoint, self).set_value(tp, val)
		if self.inputType.validate(val):
			pass
		else:
			print "Failed to validate a value of " + self.zone + '\'s Common Setpoint to ' + str(val)

	def reset_value(self,val,tp): # This is dummy for test
		super(ActualCoolingSetpoint, self).reset_value()

	def set_value_active(self, val, tp):
		super(ActualCoolingSetpoint, self).set_value(tp, val)
# ts(list of dict) -> 
		if self.inputType.validate(val):
			context = {'room':self.zone, 'template':self.template}
			uuid = self.bdm.get_sensor_uuids(context)[0]
			self.bdm.set_sensor(uuid, self.sensorType, tp, val)
		else:
			print "Failed to validate a value of " + zone + '\'s Common Setpoint to ' + str(givenVal)

	def get_value(self, beginTime, endTime):
#		return self.bdm.get_zone_sensor_ts(self.zone, self.template, self.sensorType, beginTime, endTime)
		return self.bdm.get_sensor_ts(self.uuid, self.sensorType, beginTime, endTime)

	def reset_value_active(self, val, tp):
		super(ActualCoolingSetpoint, self).reset_value()
		context = {'room':self.zone, 'template':self.template}
		uuid = self.bdm.get_sensor_uuids(context)[0]
		self.bdm.set_sensor(uuid, self.sensorType, tp, val)
	
	#TODO: Do I need this?
	def set_reset_value(self):
		pass
