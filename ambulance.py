from actuator_names import ActuatorNames
import metaactuators
from collection_wrapper import CollectionWrapper

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ntplib
from time import ctime
import csv
import pymongo
from pytz import timezone
import json
import time
import sys, os
from collection_wrapper import CollectionWrapper

import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 62122))

class Ambulance:
	resetColl = None
	expLogColl = None
	dummyBeginTime = datetime(2000,1,1)
	dummyEndTime = datetime(2030,12,31)

	def __init__(self):
		self.resetColl = CollectionWrapper('reset_queue')
		self.expLogColl = CollectionWrapper('experience_log')

	def emergent_rollback(self):
		queryAll = {'reset_time':{'$gte':self.dummyBeginTime}}
		self.resetColl.pop_data(queryAll)

