from master_actuator import Actuator 
from actuator_names import ActuatorNames
from sensor_names import SensorNames
from bd_wrapper import BDWrapper
from datetime import datetime, timedelta

#TODO: All the types of actuators classes should be implemented here with the super class, Actuator.

def make_actuator(uuid, name, zone=None, actuType=None):
	actuNames = ActuatorNames()
	if actuType==actuNames.commonSetpoint:
		return CommonSetpoint(name, uuid, 60, 80, zone)
	if actuType==actuNames.occupiedCommand:
		return OccupiedCommand(name, uuid, zone)
	if actuType==actuNames.coolingCommand:
		return CoolingCommand(name, uuid, 0,100,zone)
	if actuType==actuNames.heatingCommand:
		return HeatingCommand(name, uuid, 0,100,zone)
	if actuType==actuNames.actualSupplyFlowSP:
		#return ActualSupplyFlowSP(name, uuid, 0,500,zone) # TODO: This should be dependent on a zone
		return ActualSupplyFlowSP(name, uuid, zone)
	if actuType==actuNames.damperCommand:
		return DamperCommand(name, uuid, -0.5,0.5,zone)
	if actuType==actuNames.occupiedCoolingMinimumFlow:
		return OccupiedCoolingMinimumFlow(name, uuid, 0, 500, zone)
	if actuType==actuNames.occupiedCoolingMinimumFlow:
		return OccupiedCoolingMinimumFlow(name, uuid, 0, 500, zone)
	if actuType==actuNames.tempOccSts:
		return TempOccSts(name, uuid, zone)
	else:
		print "Failed to make an actuator: incorrect type name, " + actuType
		return None

actuNames = ActuatorNames()
sensorNames = SensorNames()

class CommonSetpoint(Actuator):
	bdm = BDWrapper()
	zone = None
	template = None

#TODO: Is it okay to set minVal and maxVal arbitrarily outside this class?
	def __init__ (self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(CommonSetpoint, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.TempType(minVal, maxVal)
		self.zone = zone
		self.template = actuNames.commonSetpoint
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		if val=='ZT':
			ztuuid = self.bdm.get_sensor_uuids({'room':self.zone, 'template':sensorNames.zoneTemperature})[0]
			now = datetime.now()
			currZT = self.bdm.get_sensor_ts(ztuuid, 'PresentValue', now-timedelta(hours=1), now).tail().tolist()[0]
			val = currZT
		else:
			pass
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
	def __init__ (self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(ActualCoolingSetpoint, self).__init__(timedelta(minutes=2))
		self.inputType = master_actuator.TempType(minVal, maxVal)
		self.zone = zone
		self.template = actuNames.actualCoolingSetpoint
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

class TempOccSts(Actuator):
	zone = None
	template = None

#TODO: Is it okay to set minVal and maxVal arbitrarily outside this class?
	def __init__ (self, name, uuid, zone):
		self.name = name
		self.uuid = uuid
		super(TempOccSts, self).__init__(timedelta(minutes=2))
		self.inputType = master_actuator.TempOcType()
		self.zone = zone
		self.template = actuNames.tempOccSts
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(TempOccSts, self).set_value(val, tp)

	def get_value(self, beginTime, endTime):
#		return self.bdm.get_zone_sensor_ts(self.zone, self.template, self.sensorType, beginTime, endTime)
		return self.bdm.get_sensor_ts(self.uuid, self.sensorType, beginTime, endTime)

	def reset_value(self, val, tp):
		super(TempOccSts, self).reset_value(val,tp)
	
	#TODO: Do I need this?
	def set_reset_value(self):
		pass

class OccupiedCommand(Actuator):
	zone = None
	template = None

#TODO: Is it okay to set minVal and maxVal arbitrarily outside this class?
	def __init__ (self, name, uuid, zone):
		self.name = name
		self.uuid = uuid
		super(OccupiedCommand, self).__init__(timedelta(minutes=2))
		self.inputType = master_actuator.OcType()
		self.zone = zone
		self.template = actuNames.occupiedCommand
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

	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(CoolingCommand, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.PercentType(minVal, maxVal)
		self.zone = zone
		self.template = actuNames.coolingCommand
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(CoolingCommand, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(CoolingCommand, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(CoolingCommand, self).get_value(beginTime, endTime)

class HeatingCommand(Actuator):
	zone = None
	template = None

	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(HeatingCommand, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.PercentType(minVal, maxVal)
		self.zone = zone
		self.template = actuNames.heatingCommand
		self.sensorType = 'PresentValue'

	def set_value(self, val, tp):
		super(HeatingCommand, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(HeatingCommand, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(HeatingCommand, self).get_value(beginTime, endTime)


class ActualSupplyFlowSP(Actuator):
	zone = None
	template = None

	#def __init__(self, name, uuid, minVal, maxVal, zone):
	def __init__(self, name, uuid, zone):
		super(ActualSupplyFlowSP, self).__init__(timedelta(minutes=10))
		self.name = name
		self.uuid = uuid
		self.zone = zone
		self.template = actuNames.actualSupplyFlowSP
		self.sensorType = 'PresentValue'
		#TODO: set the max and min by those values
		maxflowUuid = self.bdm.get_sensor_uuids({'room':zone, 'template':'Cooling Max Flow'})[0]
		minHeatingFlowUuid = self.bdm.get_sensor_uuids({'room':zone, 'template':'Occupied Htg Flow'})[0]
		minCoolingFlowUuid = self.bdm.get_sensor_uuids({'room':zone, 'template':'Occupied Clg Min'})[0]
		minVal = self.bdm.get_zone_sensor_ts(self.zone, 'Occupied Clg Min', self.sensorType, datetime.now()-timedelta(hours=1), datetime.now())[0]
		maxVal = self.bdm.get_zone_sensor_ts(self.zone, 'Cooling Max Flow', self.sensorType, datetime.now()-timedelta(hours=1), datetime.now())[0]
		#self.inputType = master_actuator.FlowType(minVal, maxVal)
		self.inputType = master_actuator.FlowType(minVal, maxVal)

	def set_value(self, val, tp):
		super(ActualSupplyFlowSP, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(ActualSupplyFlowSP, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(ActualSupplyFlowSP, self).get_value(beginTime, endTime)

class DamperCommand(Actuator):
	zone = None
	template = None
	
	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(DamperCommand, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.DamperPosType(minVal,maxVal)
		template = actuNames.damperCommand
		self.zone = zone
		self.sensorType = 'PresentValue'
	
	def set_value(self, val, tp):
		super(DamperCommand, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(DamperCommand, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(DamperCommand, self).get_value(beginTime, endTime)
	
class OccupiedCoolingMinimumFlow(Actuator):
	zone = None
	template = None
	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(OccupiedCoolingMinimumFlow, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.FlowType(0,200)
		self.zone = zone
		self.template = actuNames.occupiedCoolingMinimumFlow
		self.sensorType = 'PresentValue'
	
	def set_value(self, val, tp):
		super(OccupiedCoolingMinimumFlow, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(OccupiedCoolingMinimumFlow, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(OccupiedCoolingMinimumFlow, self).get_value(beginTime, endTime)

class CoolingMaxFlow(Actuator):
	zone = None
	template = None
	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(CoolingMaxFlow, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.FlowType(300,1000)
		self.zone = zone
		self.template = actuNames.occupiedCoolingMinimumFlow
		self.sensorType = 'PresentValue'
	
	def set_value(self, val, tp):
		super(CoolingMaxFlow, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(CoolingMaxFlow, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(CoolingMaxFlow, self).get_value(beginTime, endTime)

class OccupiedHeatingFlow(Actuator):
	zone = None
	template = None
	def __init__(self, name, uuid, minVal, maxVal, zone):
		self.name = name
		self.uuid = uuid
		super(OccupiedHeatingFlow, self).__init__(timedelta(minutes=10))
		self.inputType = master_actuator.FlowType(0,200)
		self.zone = zone
		self.template = actuNames.occupiedCoolingMinimumFlow
		self.sensorType = 'PresentValue'
	
	def set_value(self, val, tp):
		super(OccupiedHeatingFlow, self).set_value(val, tp)
	
	def reset_value(self, val, tp):
		super(OccupiedHeatingFlow, self).reset_value(val, tp)
	
	def get_value(self, beginTime, endTime):
		return super(OccupiedHeatingFlow, self).get_value(beginTime, endTime)
