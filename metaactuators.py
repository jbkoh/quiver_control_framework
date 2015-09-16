import master_actuator
reload(master_actuator)
from master_actuator import Actuator 
import actuator_names
reload(actuator_names)
from actuator_names import ActuatorNames

from datetime import datetime, timedelta

import requests


#TODO: All the types of actuators classes should be implemented here with the super class, Actuator.


def make_actuator(uuid, name, zone=None, actuType=None):
	actuNames = ActuatorNames()
	if actuType==actuNames.commonSetpoint:
		return CommonSetpoint(name, uuid, 66,74,zone)
	if actuType==actuNames.occupiedCommand:
		return OccupiedCommand(name, uuid, zone)
	if actuType==actuNames.coolingCommand:
		return CoolingCommand(name, uuid, 0,100,zone)
	if actuType==actuNames.heatingCommand:
		return HeatingCommand(name, uuid, 0,100,zone)
	if actuType==actuNames.actualSupplyFlowSP:
		return ActualSupplyFlowSP(name, uuid, 0,500,zone) # TODO: This should be dependent on a zone
	if actuType==actuNames.damperCommand:
		return DamperCommand(name, uuid, -0.5,0.5,zone)
	if actuType==actuNames.occupiedCoolingMinimumFlow:
		return occupiedCoolingMinimumFlow(name, uuid, 0, 500, zone)
	else:
		print "Failed to make an actuator: incorrect type name, " + actuType
		return None

class CommonSetpoint(Actuator):
	zone = None
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
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(CommonSetpoint, self).set_value(val, tp+timedelta(minutes=1))
	
	def get_value(self, beginTime, endTime):
		return super(CommonSetpoint, self).get_value(beginTime, endTime)

	def reset_value(self, val, tp):
		super(CommonSetpoint, self).reset_value(val, tp)
	
	#TODO: Do I need this?
	def set_reset_value(self, resetVal=-1):
		self.resetVal = resetVal

class ActualCoolingSetpoint(Actuator):
	zone = None
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
		self.sensorType = 'PresentValue'

	def set_value_void(self, val, tp): # This is dummy for test
		super(ActualCoolingSetpoint, self).set_value(val, tp)
		if self.inputType.validate(val):
			pass
		else:
			print "Failed to validate a value of " + self.zone + '\'s Common Setpoint to ' + str(val)

	def reset_value_void(self,val,tp): # This is dummy for test
		super(ActualCoolingSetpoint, self).reset_value()

	def set_value(self, val, tp):
		super(ActualCoolingSetpoint, self).set_value(val, tp)

	def get_value(self, beginTime, endTime):
#		return self.bdm.get_zone_sensor_ts(self.zone, self.template, self.sensorType, beginTime, endTime)
		return self.bdm.get_sensor_ts(self.uuid, self.sensorType, beginTime, endTime)

	def reset_value(self, val, tp):
		super(ActualCoolingSetpoint, self).reset_value(val, tp)
	
	#TODO: Do I need this?
	def set_reset_value(self):
		pass

class OccupiedCommand(Actuator):
	zone = None
	template = None
	actuNames = ActuatorNames()

#TODO: Is it okay to set minVal and maxVal arbitrarily outside this class?
	def __init__ (self, name, uuid, zone):
		self.name = name
		self.uuid = uuid
		super(OccupiedCommand, self).__init__(timedelta(minutes=2))
		self.inputType = master_actuator.OcType()
		self.zone = zone
		self.template = self.actuNames.occupiedCommand
		self.sensorType = 'PresentValue'

	def set_value_void(self, val, tp): # This is dummy for test
		super(OccupiedCommand, self).set_value(val, tp)
		if self.inputType.validate(val):
			pass
		else:
			print "Failed to validate a value of " + self.zone + '\'s Common Setpoint to ' + str(val)

	def reset_value_void(self,val,tp): # This is dummy for test
		super(OccupiedCommand, self).reset_value(val, tp)

	def set_value(self, val, tp):
		super(OccupiedCommand, self).set_value(val, tp)

	def get_value(self, beginTime, endTime):
#		return self.bdm.get_zone_sensor_ts(self.zone, self.template, self.sensorType, beginTime, endTime)
		return self.bdm.get_sensor_ts(self.uuid, self.sensorType, beginTime, endTime)

	def reset_value(self, val, tp):
		super(OccupiedCommand, self).reset_value(val,tp)
	
	#TODO: Do I need this?
	def set_reset_value(self):
		pass

class CoolingCommand(Actuator):
	zone = None
	template = None
	actuNames = ActuatorNames()

	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(CoolingCommand, self).__init__(timedelta(minutes=5))
		self.inputType = master_actuator.PercentType(minVal, maxVal)
		self.zone = zone
		self.template = self.actuNames.coolingCommand
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(CoolingCommand, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(CoolingCommand, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		super(CoolingCommand, self).get_value(beginTime, endTime)

class HeatingCommand(Actuator):
	zone = None
	template = None
	actuNames = ActuatorNames()

	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(HeatingCommand, self).__init__(timedelta(minutes=5))
		self.inputType = master_actuator.PercentType(minVal, maxVal)
		self.zone = zone
		self.template = self.actuNames.heatingCommand
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(HeatingCommand, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(HeatingCommand, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		super(HeatingCommand, self).get_value(beginTime, endTime)

actuNames = ActuatorNames()

class ActualSupplyFlowSP(Actuator):
	zone = None
	template = None
	actuNames = ActuatorNames()

	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(ActualSupplyFlowSP, self).__init__(timedelta(minutes=5))
		self.inputType = master_actuator.FlowType(minVal, maxVal)
		self.zone = zone
		self.template = self.actuNames.actualSupplyFlowSP
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(ActualSupplyFlowSP, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(ActualSupplyFlowSP, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		super(ActualSupplyFlowSP, self).get_value(beginTime, endTime)

class DamperCommand(Actuator):
	zone = None
	template = None
	
	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(DamperCommand, self).__init__(timedelta(minutes=1))
		self.inputType = master_actuator.DamperPosType(minVal,maxVal)
		template = actuNames.damperCommand
		self.zone = zone
		self.sensorType = 'PresentValue'
	
	def set_value(self, val, tp):
		super(DamperCommand, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(DamperCommand, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		super(DamperCommand, self).get_value(beginTime, endTime)
	
class OccupiedCoolingMinimumFlow(Actuator):
	zone = None
	template = None
	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(OccupiedCoolingMinimumFlow, self).__init__(timedelta(minutes=5))
		self.inputType = master_actuator.FlowType(0,500)
		self.zone = zone
		self.template = actuNames.occupiedCoolingMinimumFlow
		self.sensorType = 'PresentValue'
	
	def set_value(self, val, tp):
		super(OccupiedCoolingMinimumFlow, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(OccupiedCoolingMinimumFlow, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		super(OccupiedCoolingMinimumFlow, self).get_value(beginTime, endTime)
