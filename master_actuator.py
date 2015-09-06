from enum import Enum
from abc import ABCMeta, abstractmethod
from bd_wrapper import BDWrapper


# default occupied command type
#class oc_struct(Enum):
#	unouccupied = 1
#	standby = 2
#	occupied = 3
#
class DefaultType(object):
	minVal = None
	maxVal = None
	hardMinVal = None
	hardMaxVal = None

	def __init__(self, hardMinVal, hardMaxVal, minVal, maxVal):
		self.hardMinVal = hardMinVal
		self.hardMaxVal = hardMaxVal
		# TODO: Raise error here!!!!
		if minVal<self.hardMinVal:
			print "min value is not valid in initialization"
#			raise Error
		elif maxVal > self.hardMaxVal:
			print "max value is not valid in initialization"
#			raise Error
		self.minVal = minVal
		self.maxVal = maxVal

	def validate(self, given):
		if given <=self.maxVal and given>=self.minVal:
			return True
		else:
			return False

class OcType(DefaultType):
	commands = (1,2,3) #1=unoccupied, 2=standby, 3=occupied

	def __init__(self):
		pass

	def validate(self,given):
		if given in self.commands:
			return True
		else:
			return False

class DamperPosType(DefaultType):
	def __init__(self, minVal, maxVal):
		super(FlowType, self).__init__(-3,3,minVal,maxVal)
		#TODO Is hardMaxVal correct for damperPos type?

	def validate(self, given):
		super(FlowType,self).validate(given)

class FlowType(DefaultType):
	minVal = None
	maxVal = None
	def __init__(self, minVal, maxVal):
		super(FlowType, self).__init__(0,3000,minVal,maxVal)
		#TODO Is hardMaxVal correct for flow type?

	def validate(self, given):
		super(FlowType,self).validate(given)

class TempType(DefaultType):
	minVal = None
	maxVal = None
	def __init__(self, minVal, maxVal):
		super(FlowType, self).__init__(50,90,minVal,maxVal)
		#TODO Is hardMaxVal correct for temp type?

	def validate(self, given):
		super(FlowType,self).validate(given)

class PercentType(DefaultType):
	minVal = None
	maxVal = None
	def __init__(self, minVal, maxVal):
		super(FlowType, self).__init__(0,100,minVal,maxVal)

	def validate(self, given):
		super(FlowType,self).validate(given)
	

class Actuator(object):
	__metaclass__ = ABCMeta
	minLatency = None # 0 minimum
	inputType = None # should be selected among above type classes
	lowerActuators = list() 
	higherActuators = list()
	dependentList = list()
	controlFlag = False
	uuid = None
	name = None
	bdm = None
	sensorType = None

	def __init__(self, minLatency):
# minLatency(datetime) ->
		self.minLatency = minLatency
		self.bdm = BDWrapper()

	@abstractmethod
	def set_value(self, val, tp):
		self.controlFlag = True
		if self.inputType.validate(val):
			self.bdm.set_sensor(self.uuid, self.sensorType, tp, val)
		else:
			print "Failed to validate a value of " + self.zone + '\'s Common Setpoint to ' + str(givenVal)

	@abstractmethod
	def get_value(self, beginTime, endTime):
		return self.bdm.get_sensor_ts(self.uuid, self.sensorType, beginTime, endTime)

	@abstractmethod #Should this be abm?
	def reset_value(self, val, tp):
		self.bdm.set_sensor(self.uuid, self.sensorType, tp, val)
		self.controlFlag = False
	
	def check_control_flag(self):
		return self.controlFlag

	def check_dependency(self, actuType):
		if actuType in self.dependentList:
			return True
		else:
			return False
	def validate_input(self, given):
		return self.inputType.validate(given)

	
