import csv
import pandas as pd
from datetime import datetime, timedelta
from actuator_names import ActuatorNames
import metaactuators

class Exper:

	inputTimeFormat = '%Y-%m-%d %H:%M:%S'
	actuDict= dict()
	actuNames = ActuatorNames()

	def __init__(self):
		pass

	def seq_read(self, filename):
# filename(string, excel) -> seqList(pd.DataFrame)
		seqList = pd.read_excel(filename)
		for row in seqList.iterrows():
			zone = row[1]['zone']
			actuatorType = row[1]['actuator_type']
			if not self.actuator_exist(zone, template):
				oneActu = metaactuators.make_actuator(zone,actuatorType)
				if oneActu:
					self.actuDict[[zone, actuatorType]] = oneActu
		seqList['timestamp'] = datetime.strptime(seqList['timestamp'], self.inputTimeFormat)
		return seqList

	def actuator_exist(self, zone, actuatorType):
# zone(string), actuatortype(string) -> existing?(boolean)
		if [zone, actuatorType] in self.actuDict.keys():
			return True
		else:
			return False

	def validate_exp_seq_freq(self,seq):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			actuator  = self.actuDict[[zone, actuType]]
			minLatency = actuator.minLatency
			tp = row[1]['timestamp']
			inrangeRows = np.bitwise_and(seq['timestamp']<tp+minLatency, seq['timestamp']>tp-minLatency)
			inrangeRows = seq.iloc[inrangeRows]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and inrangeRow[1]['actuator_type']==actuType:
					print baseInvalidMsg + str(row[1]) + ' is overlapped with ' + str(inrangeRow[1])
					return False
		return True
	
	def validate_exp_seq_dependency(self, seq, minExpLatency):
# seq(pd.DataFrame) -> valid?(boolean)
		baseInvalidMsg = "Test sequence is invalid because "
		for row in seq.iterrows():
			zone = row[1]['zone']
			actuType = row[1]['actuator_type']
			actuator  = self.actuDict[[zone, actuType]]
			minLatency = actuator.minLatency
			tp = row[1]['timestamp']
			inrangeRowaIdx = np.bitwise_and(seq['timestamp']<tp, seq['timestamp']>=tp-minExpLatency)
			inrangeRows = seq.iloc[inrangeRowsIdx]
			for inrangeRow in inrangeRows.iterrows():
				if inrangeRow[1]['zone']==zone and actuator.check_dependency(inrangeRow[1]['actuator_type']):
					print baseInvalidMsg + str(row[1]) + ' is dependent on ' str(inrangeRow[1])
					return False
		return True

	def validate_exp_seq(self, seq):
		self.validate_exp_seq_freq(self,seq)
		self.validate_exp_seq_dependency(self,seq)
