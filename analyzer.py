from bd_wrapper import BDWrapper
from collection_wrapper import CollectionWrapper

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class analyzer:
	bdm = None
	expLogColl = None

	def __init__(self):
		self.bdm = BDWrapper
		self.expLogColl = CollectionWrapper('experience_log')

