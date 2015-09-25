from enum import Enum
from abc import ABCMeta, abstractmethod
from bd_wrapper import BDWrapper
from datetime import datetime, timedelta
import pickle


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
		if (given <=self.maxVal and given>=self.minVal) or given==-1:
			return True
		else:
			return False

class OcType(DefaultType):
	commands = (1,2,3) #1=unoccupied, 2=standby, 3=occupied

	def __init__(self):
		pass

	def validate(self,given):
		if given in self.commands or given==-1:
			return True
		else:
			return False

class DamperPosType(DefaultType):
	def __init__(self, minVal, maxVal):
		super(DamperPosType, self).__init__(-2,2,minVal,maxVal)
		#TODO Is hardMaxVal correct for damperPos type?

	def validate(self, given):
		return super(DamperPosType,self).validate(given)

class FlowType(DefaultType):
	def __init__(self, minVal, maxVal):
		super(FlowType, self).__init__(0,3000,minVal,maxVal)
		#TODO Is hardMaxVal correct for flow type?

	def validate(self, given):
		return super(FlowType,self).validate(given)

class TempType(DefaultType):
	def __init__(self, minVal, maxVal):
		super(TempType, self).__init__(50,90,minVal,maxVal)
		#TODO Is hardMaxVal correct for temp type?

	def validate(self, given):
		return super(TempType,self).validate(given)

class PercentType(DefaultType):
	def __init__(self, minVal, maxVal):
		super(PercentType, self).__init__(0,100,minVal,maxVal)

	def validate(self, given):
		return super(PercentType,self).validate(given)

class Actuator(object):
	__metaclass__ = ABCMeta
	minLatency = None # 0 minimum
	inputType = None # should be selected among above type classes
	lowerActuators = list() 
	higherActuators = list()
	affectingDependencyDict = dict() # values of this dict are each actuator's minLatency
	affectedDependencyDict = dict() # values of this dict are this actuator's minLatency
	controlFlag = False
	uuid = None
	name = None
	bdm = None
	sensorType = None
	resetVal = None
	depMapFile = 'metadata/dependency_map.pkl'

	def __init__(self, minLatency):
# minLatency(datetime) ->
		self.minLatency = minLatency
		self.bdm = BDWrapper()
		depMap = pickle.load(open(self.depMapFile, 'rb'))
		if self.uuid in depMap.keys():
			for depUuid in depMap[self.uuid]:
				self.affectingDependencyDict[depUuid] = timedelta(minutes=10)
				self.affectedDependencyDict[depUuid] = timedelta(minutes=10)

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

	def get_latest_value(self, now):
		result = self.bdm.get_sensor_ts(self.uuid, self.sensorType, now-timedelta(hours=6), now+timedelta(minutes=10))
		if result.empty:
			return None
		else:
			return result.tail(1).values[0], result.tail(1).index[0]
	
	def get_second_latest_value(self,now):
		result = self.bdm.get_sensor_ts(self.uuid, self.sensorType, now-timedelta(hours=6), now+timedelta(minutes=10))
		if len(result)<=1:
			return None
		else:
			return result.tail(2).values[1], result.tail(2).index[1]
	
	def check_control_flag(self):
		return self.controlFlag

	def check_dependency(self, commDict, setTime):
		if (commDict['set_time']> setTime-self.minLatency) and commDict['uuid']==self.uuid:
			return True
		else:
			return False
		

	def get_dependency(self, uuid):
		if uuid in self.affectingDependencyDict.keys():
			return self.affectingDependencyDict[uuid]
		elif uuid in self.affectedDependencyDict.keys():
			return self.affectedDependencyDict[uuid]
		else:
			return None
	
	def get_dependent_actu_list(self):
		return self.affectingDependencyDict.keys() + self.affectedDependencyDict.keys()
	
	def get_longest_dependency(self):
		return max(max(self.affectedDependencyDict.values()),max(self.affectingDependencyDict.values()))

	def validate_input(self, given):
		return self.inputType.validate(given)

	
