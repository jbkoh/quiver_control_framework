from enum import Enum
from abc import ABCMeta


# default occupied command type
#class oc_struct(Enum):
#	unouccupied = 1
#	standby = 2
#	occupied = 3
#
class oc_type():
	commands = (1,2,3) #1=unoccupied, 2=standby, 3=occupied

	def validate(self,given):
		if gigen in commands:
			return True
		else:
			return False

class temp_type():
	minVal = None
	maxVal = None

	def __init__(self, minVal, maxVal):
		self.minVal = minVal
		self.maxVal = maxVal

	def validate(self, given):
		if given <=maxVal and given>=minVal:
			return True
		else:
			return False

class master_actuator:
	__metaclass__ = ABCMeta
	latency_min = None # 0 minimum

	inputType = None # should be selected among above type classes

	def __init__(self):
		pass

	@abstractmethod
	def set_value(self):
		pass

	@abstractmethod
	def get_value(self):
		pass

	@abstractmethod #Should this be abm?
	def reset_value(self):
		pass

	
