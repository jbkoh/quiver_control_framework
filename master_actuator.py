from enum import Enum
from abc import ABCMeta, abstractmethod


# default occupied command type
#class oc_struct(Enum):
#	unouccupied = 1
#	standby = 2
#	occupied = 3
#
class OcType():
	commands = (1,2,3) #1=unoccupied, 2=standby, 3=occupied

	def validate(self,given):
		if given in commands:
			return True
		else:
			return False

class TempType():
	minVal = None
	maxVal = None

	def __init__(self, minVal, maxVal):
		self.minVal = minVal
		self.maxVal = maxVal

	def validate(self, given):
		if given <=self.maxVal and given>=self.minVal:
			return True
		else:
			return False

class Actuator:
	__metaclass__ = ABCMeta
	minLatency = None # 0 minimum
	inputType = None # should be selected among above type classes
	lowerActuators = list() 
	higherActuators = list()
	dependentList = list()
	controlFlag = False
	uuid = None
	name = None

	def __init__(self, minLatency):
# minLatency(datetime) ->
		self.minLatency = minLatency

	@abstractmethod
	def set_value(self, tp, val):
		self.controlFlag = True

	@abstractmethod
	def get_value(self, beginTime, endTime):
#beginTime(datetime), endTime(datetime) -> pdts
		pass

	@abstractmethod #Should this be abm?
	def reset_value(self):
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

	
