from analyzer import Analyzer

from datetime import datetime

anal = Analyzer()

zonelist = ['RM-2226', 'RM-2230']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,12,22,30),datetime(2015,10,13,0,10), 'nextval', 'data/dep/dep_cs_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,0,10),datetime(2015,10,13,1,10), 'nextval', 'data/dep/dep_oc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,1,20),datetime(2015,10,13,2,50), 'nextval', 'data/dep/dep_asfsp_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,2,50),datetime(2015,10,13,4,30), 'nextval', 'data/dep/dep_dc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,4,50),datetime(2015,10,13,5,50), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,4,50),datetime(2015,10,13,5,50), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1012.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,6,10),datetime(2015,10,13,7,50), 'nextval', 'data/dep/dep_cc_'+zone.replace('RM-','')+'_1012.pkl')

zonelist = ['RM-2226', 'RM-2230']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,13,21,40),datetime(2015,10,13,23,45), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1013.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,13,21,50),datetime(2015,10,14,1,45), 'nextval', 'data/dep/dep_dc_'+zone.replace('RM-','')+'_1013.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,14,3,20),datetime(2015,10,14,4,30), 'nextval', 'data/dep/dep_asfsp_'+zone.replace('RM-','')+'_1013.pkl')

zonelist = ['RM-2226', 'RM-2230']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,14,14,30),datetime(2015,10,14,17,20), 'nextval', 'data/dep/dep_cc_'+zone.replace('RM-','')+'_1014.pkl')

zonelist = ['RM-2112', 'RM-2108', 'RM-2118']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,15,23,55),datetime(2015,10,16,3,30), 'nextval', 'data/dep/dep_cs_'+zone.replace('RM-','')+'_1015.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,16,0,55),datetime(2015,10,16,2,10), 'nextval', 'data/dep/dep_oc_'+zone.replace('RM-','')+'_1015.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,16,2,10),datetime(2015,10,16,4,30), 'nextval', 'data/dep/dep_cc_'+zone.replace('RM-','')+'_1015.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,16,4,50),datetime(2015,10,16,7,30), 'nextval', 'data/dep/dep_hc_'+zone.replace('RM-','')+'_1015.pkl')

zonelist = ['RM-2112', 'RM-2108', 'RM-2118']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,16,20,30),datetime(2015,10,16,22,10), 'nextval', 'data/dep/dep_cs_'+zone.replace('RM-','')+'_1016.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,16,22,12),datetime(2015,10,17,1,8), 'nextval', 'data/dep/dep_oc_'+zone.replace('RM-','')+'_1016.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,17,1,10),datetime(2015,10,17,4,40), 'nextval', 'data/dep/dep_cc_'+zone.replace('RM-','')+'_1016.pkl')

zonelist = ['RM-2112', 'RM-2108', 'RM-2118', 'RM-2226', 'RM-2230']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,16,20,30),datetime(2015,10,16,22,10), 'nextval', 'data/dep/dep_cs_'+zone.replace('RM-','')+'_1017.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,16,22,14),datetime(2015,10,17,1,10), 'nextval', 'data/dep/dep_oc_'+zone.replace('RM-','')+'_1017.pkl')
	anal.store_zone_sensors(zone, datetime(2015,10,17,1,10),datetime(2015,10,17,4,25), 'nextval', 'data/dep/dep_cc_'+zone.replace('RM-','')+'_1017.pkl')


zonelist = ['RM-2112', 'RM-2108', 'RM-2118', 'RM-2226', 'RM-2230']
for zone in zonelist:
	anal.store_zone_sensors(zone, datetime(2015,10,18,18,30),datetime(2015,10,18,19,40), 'nextval', 'data/dep/dep_acfsp_'+zone.replace('RM-','')+'_1018.pkl')
