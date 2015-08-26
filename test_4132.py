import bd_wrapper
reload(bd_wrapper)
from bd_wrapper import bd_wrapper
from datetime import datetime
import pdb



bdm = bd_wrapper()
context = {'room':'rm-4132', 'template':'Common Setpoint'}
uuid = bdm.get_sensor_uuids(context)[0]
print uuid

try:
	ts = bdm.get_zone_sensor_ts('4132','Zone Temperature', 'PresentValue', datetime(2015,8,24,0,0,0),datetime(2015,8,25,0,0,0))
	print ts
except:
	pdb.run("bdm.get_zone_sensor_ts('4132','Zone Temperature', 'PresentValue', datetime(2015,8,24,0,0,0),datetime(2015,8,25,0,0,0))")

#ts = [{datetime(2015,8,26,xx,x,x):78}]
#bdm.set_sensor_ts(uuid, 'PresentValue', 
