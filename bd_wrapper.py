from building_depot import DataService, BDError
import authdata

import datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import numpy as np


#Example of time init
# self.pst.localize(offTime, is_dst=True)


class bd_wrapper:

	bdDS = None
	pst = timezone('US/Pacific')

	def __init__(self):
		self.bdDS = DataService(authdata.srcUrlBaes, authdata.bdApiKey, authdata.bdUserName)

	def 
