from analyzer import Analyzer

from datetime import datetime

anal = Analyzer()

zonelist = ['RM-2226', 'RM-2230']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,12,22,30),datetime(2015,10,13,0,10), 'nextval', 'data/dep/dep_oc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,0,10),datetime(2015,10,13,1,10), 'nextval', 'data/dep/dep_cs_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,1,20),datetime(2015,10,13,2,50), 'nextval', 'data/dep/dep_safs_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,2,50),datetime(2015,10,13,4,30), 'nextval', 'data/dep/dep_dc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,4,50),datetime(2015,10,13,5,50), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,4,50),datetime(2015,10,13,5,50), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,6,10),datetime(2015,10,13,7,50), 'nextval', 'data/dep/dep_cc_'+zone.replace('RM-','')+'_1012.pkl')

for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,13,21,40),datetime(2015,10,13,23,45), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1013.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,21,40),datetime(2015,10,13,23,45), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1013.pkl')
