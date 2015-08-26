import bd_wrapper
reload(bd_wrapper)
from bd_wrapper import bd_wrapper
from datetime import datetime
import pdb



bdm = bd_wrapper()

#Get data test
context = {'room':'rm-4132', 'template':'Common Setpoint'}
uuid = bdm.get_sensor_uuids(context)[0]
print uuid

ts = bdm.get_zone_sensor_ts('4132','Common Setpoint', 'PresentValue', datetime(2015,8,26,11,17,0),datetime(2015,8,26,11,40,0))
print ts


# Put data test
context = {'room':'rm-4132', 'template':'Common Setpoint'}
uuid = bdm.get_sensor_uuids(context)[0]
print uuid
ts = [{datetime(2015,8,26,11,22,32):72}]
print bdm.set_sensor_latest(uuid, 'PresentValue', 70)
#bdm.set_sensor_ts(uuid, 'PresentValue', ts)
print 'Finish'
