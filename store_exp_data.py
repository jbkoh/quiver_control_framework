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
#anal.store_zone_sensors('RM-3148', datetime(2015,10,5,20,30), datetime(2015,10,6,5,00), 'nextval', 'data/dep_cs_3148_1005.pkl')
#anal.store_zone_sensors('RM-3142', datetime(2015,10,6,5,45), datetime(2015,10,6,9,15), 'nextval', 'data/dep_cs_3142_1005_2.pkl')
anal.store_zone_sensors('RM-3142', datetime(2015,10,5,20,30), datetime(2015,10,6,9,15), 'nextval', 'data/dep_cs_3142_1005.pkl')
anal.store_zone_sensors('RM-3148', datetime(2015,10,6,5,45), datetime(2015,10,6,9,15), 'nextval', 'data/dep_cs_3148_1005_2.pkl')
anal.store_zone_sensors('RM-3150', datetime(2015,10,5,20,00), datetime(2015,10,6,1,30), 'nextval', 'data/dep_oc_3150_1005.pkl')
anal.store_zone_sensors('RM-3152', datetime(2015,10,5,20,00), datetime(2015,10,6,1,30), 'nextval', 'data/dep_oc_3152_1005.pkl')
anal.store_zone_sensors('RM-3252', datetime(2015,10,5,20,45), datetime(2015,10,5,23,45), 'nextval', 'data/dep_cc_3252_1005.pkl')
anal.store_zone_sensors('RM-3252', datetime(2015,10,5,23,52), datetime(2015,10,6,3,15), 'nextval', 'data/dep_hc_3252_1005.pkl')
anal.store_zone_sensors('RM-3256', datetime(2015,10,5,20,45), datetime(2015,10,5,23,45), 'nextval', 'data/dep_cc_3256_1005.pkl')
anal.store_zone_sensors('RM-3256', datetime(2015,10,5,23,52), datetime(2015,10,6,3,15), 'nextval', 'data/dep_hc_3256_1005.pkl')

#10/07
#anal.store_zone_sensors('RM-3256', datetime(2015,10,6,22,0), datetime(2015,10,7,8,14), 'nextval', 'data/reg_safsp_3256_1006.pkl')
anal.store_zone_sensors('RM-3256', datetime(2015,10,6,22,0), datetime(2015,10,7,5,30), 'nextval', 'data/reg_safsp_3256_1006.pkl')
anal.store_zone_sensors('RM-3258', datetime(2015,10,6,22,0), datetime(2015,10,7,8,14), 'nextval', 'data/reg_safsp_3258_1006.pkl')
anal.store_zone_sensors('RM-3262', datetime(2015,10,6,20,45), datetime(2015,10,7,5,0), 'nextval', 'data/reg_cc_3262_1006.pkl')
anal.store_zone_sensors('RM-3260', datetime(2015,10,6,20,45), datetime(2015,10,7,5,0), 'nextval', 'data/reg_cc_3260_1006.pkl')
anal.store_zone_sensors('RM-3144', datetime(2015,10,6,19,50), datetime(2015,10,7,3,20), 'nextval', 'data/dep_asfsp_3144_1006.pkl')
anal.store_zone_sensors('RM-3148', datetime(2015,10,6,19,50), datetime(2015,10,7,3,20), 'nextval', 'data/dep_asfsp_3148_1006.pkl')
anal.receive_entire_sensors(datetime(2015,10,6,21,0), datetime(2015,10,7,2,59), 'nextval', 'data/col_hc_3232_1006.pkl') #3232 and 3252 received commands
anal.receive_entire_sensors(datetime(2015,10,6,21,0), datetime(2015,10,7,2,59), 'nextval', 'data/col_cc_3152_1006.pkl') #3150 and 3152 received commands
