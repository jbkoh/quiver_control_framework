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

import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 62122))

class Ambulance:
	resetColl = None
	def __init__(self):
		pass





class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

server = SimpleXMLRPCServer(('localhost',62122), requestHandler=RequestHandler, allow_none=True)
server.register_introspection_functions()


def emergent_rollback(resetColl, logColl):
	print "Emergent rollback is requested"
	print resetColl
	print logColl
	print "Finish rollback"

server.register_function(emergent_rollback, 'emergent_rollback')

print 'server is ready'
#server.serve_forever()
	

#class Ambulance(rpyc.Service):
#	ntpURL = 'ntp.ucsd.edu'
#	timeOffset = timedelta(0)
#	ntpClient = None
#	inputTimeFormat = '%m/%d/%Y %H:%M:%S'
#	actuDict= dict()
#	actuNames = ActuatorNames()
#	logColl = None	 		# This is a collection for log of control. If a command is issued, it is added to here with relevant information.
#	resetColl = None		# This is a collection for rollback. If a command is issued, its corresponding rollback command is added here.
#	relinquishVal = -1
#
#	def __init__(self):
#		pass
#	
#	def on_connect(self):
#		print "Connection established"
#	def on_disconnect(Self):
#		print "Disconnection established"
#
#	def exposed_emergent_rollback(self):
#		pass
#
#	def exposed_enroll_reset_collection(self, resetColl):
#		self.resetColl = resetColl
#	def exposed_enroll_log_collection(self, logColl):
#		self.logColl = logColl
#
#try:
#	if __name__ =='__main__':
#		print 'Init server'
#		server = ThreadedServer(Ambulance, hostname='localhost', port=62122)
#		print "Server established"
#		server.start()
#		print "Server started"
#		while(1):
#			pass
#except:
#	print sys.exc_info()[0]
#	server.close()
#	print "Server closed"

