from analyzer import Analyzer

from datetime import datetime

anal = Analyzer()

# Uncontrolled Test Data
# CC
anal.store_zone_sensors('RM-3152', datetime(2014,7,1),datetime(2015,1,1),'nextval', 'data/oneyear_3152_0101.pkl')
# ASFSP
anal.store_zone_sensors('RM-3256', datetime(2014,1,1),datetime(2015,1,1),'nextval', 'data/oneyear_3256_0101.pkl')



#10/01
anal.store_zone_sensors('RM-3152', datetime(2015,10,1,18),datetime(2015,10,2,6,30),'nextval', 'data/reg_cc_3152_1001.pkl')

# Uncontrolled Regression Learning Data
# ACS/AHS
anal.store_zone_sensors('RM-2142', datetime(2015,8,1), datetime(2015,8,30), 'nextval', 'data/onemonth_2142_0801.pkl')
# CC
anal.store_zone_sensors('RM-3152', datetime(2015,9,1),datetime(2015,9,30),'nextval', 'data/onemonth_3152_0901.pkl')
# ASFSP
anal.store_zone_sensors('RM-3256', datetime(2015,9,1),datetime(2015,9,30),'nextval', 'data/onemonth_3256_0901.pkl')



#10/06
anal.store_zone_sensors('RM-3142', datetime(2015,10,5,20,30), datetime(2015,10,6,5,00), 'nextval', 'data/dep_cs_3142_1005.pkl')
anal.store_zone_sensors('RM-3148', datetime(2015,10,5,20,30), datetime(2015,10,6,5,00), 'nextval', 'data/dep_cs_3148_1005.pkl')
anal.store_zone_sensors('RM-3142', datetime(2015,10,6,5,45), datetime(2015,10,6,9,15), 'nextval', 'data/dep_cs_3142_1005_2.pkl')
anal.store_zone_sensors('RM-3148', datetime(2015,10,6,5,45), datetime(2015,10,6,9,15), 'nextval', 'data/dep_cs_3148_1005_2.pkl')
anal.store_zone_sensors('RM-3150', datetime(2015,10,5,20,00), datetime(2015,10,6,1,30), 'nextval', 'data/dep_oc_3150_1005.pkl')
anal.store_zone_sensors('RM-3152', datetime(2015,10,5,20,00), datetime(2015,10,6,1,30), 'nextval', 'data/dep_oc_3152_1005.pkl')
anal.store_zone_sensors('RM-3252', datetime(2015,10,5,20,45), datetime(2015,10,5,23,45), 'nextval', 'data/dep_cc_3252_1005.pkl')
anal.store_zone_sensors('RM-3252', datetime(2015,10,5,23,52), datetime(2015,10,6,3,15), 'nextval', 'data/dep_hc_3252_1005.pkl')
anal.store_zone_sensors('RM-3256', datetime(2015,10,5,20,45), datetime(2015,10,5,23,45), 'nextval', 'data/dep_cc_3256_1005.pkl')
anal.store_zone_sensors('RM-3256', datetime(2015,10,5,23,52), datetime(2015,10,6,3,15), 'nextval', 'data/dep_hc_3256_1005.pkl')
