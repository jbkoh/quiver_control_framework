from analyzer import Analyzer
from bd_wrapper import BDWrapper
from datetime import datetime, timedelta
import time
import sys

anal = Analyzer()
bdm = BDWrapper()
ocVal = 3

print "Will set all OCs to: ", ocVal
time.sleep(10)

for zone in anal.zonelist:
	try:
		uuid = anal.get_actuator_uuid(zone, 'Occupied Command')
		bdm.set_sensor(uuid, 'PresentValue', datetime.now()-timedelta(seconds=30), ocVal)
		print "Done: ", uuid
		time.sleep(10)
	except:
		e = sys.exc_info()[0]
		print ( "<p>Error: %s</p>" % e )


print "Finished"
