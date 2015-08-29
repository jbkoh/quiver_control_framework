import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import ntplib
from time import ctime


class runtime:
	ntpURL = 'ntp.ucsd.edu'
	timeOffset = timedelta(0)
	ntpClient = None

	def __init__(self):
		self.ntpClient = ntplib.NTPClient()
		pass

	def update_offset(self):
		ntpRequest = self.ntpClient.request(self.ntpURL)
		ntpRequest.tx_time
		ntpTime = datetime.strptime(time.ctime(ntpRequest.tx_time), "%a %b %d %H:%M:%S %Y")
		self.timeOffset = ntpTime - datetime.now()

	def issue_command(self, command):
		pass
