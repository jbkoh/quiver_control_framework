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
anal.receive_entire_sensors(datetime(2015,10,6,21,0), datetime(2015,10,7,2,59), 'data/col_hc_3232_1006.pkl', 'nextval') #3232 and 3252 received commands
anal.receive_entire_sensors(datetime(2015,10,6,21,0), datetime(2015,10,7,2,59), 'data/col_cc_3152_1006.pkl', 'nextval') #3150 and 3152 received commands


#10/08
anal.receive_entire_sensors(datetime(2015,10,7,19,32), datetime(2015,10,8,4,0), 'data/col_cc_3150_1008.pkl', 'nextval') #3150 and 3152 received commands
anal.receive_entire_sensors(datetime(2015,10,7,20,0), datetime(2015,10,8,4,0), 'data/col_hc_2112_1008.pkl', 'nextval') #3150 and 3152 received commands
anal.receive_entire_sensors(datetime(2015,10,7,19,30), datetime(2015,10,8,7,40), 'data/col_cs_3148_1008.pkl', 'nextval') #3150 and 3152 received commands
anal.store_zone_sensors('RM-3242', datetime(2015,10,7,19,50), datetime(2015,10,8,9,40), 'nextval', 'data/reg_acsahs_3242_1008.pkl')

#10/09
anal.store_zone_sensors('RM-2108', datetime(2015,10,8,19,00), datetime(2015,10,9,1,0), 'nextval', 'data/dep_oc_2108_1008.pkl')
anal.store_zone_sensors('RM-2130', datetime(2015,10,8,19,00), datetime(2015,10,9,1,0), 'nextval', 'data/dep_oc_2130_1008.pkl')
anal.store_zone_sensors('RM-4208', datetime(2015,10,8,19,00), datetime(2015,10,9,1,45), 'nextval', 'data/dep_dc_4208_1008.pkl')
anal.store_zone_sensors('RM-4220', datetime(2015,10,8,19,00), datetime(2015,10,9,1,45), 'nextval', 'data/dep_dc_4220_1008.pkl')
anal.store_zone_sensors('RM-2112', datetime(2015,10,8,19,10), datetime(2015,10,9,1,30), 'nextval', 'data/dep_hc_2112_1008.pkl')
anal.store_zone_sensors('RM-2116', datetime(2015,10,8,19,10), datetime(2015,10,9,1,30), 'nextval', 'data/dep_hc_2116_1008.pkl')
anal.receive_entire_sensors(datetime(2015,10,8,19,10), datetime(2015,10,9,0,45), 'data/col_safsp_2114_1008.pkl', 'nextval')
anal.receive_entire_sensors(datetime(2015,10,8,19,30), datetime(2015,10,9,4,0), 'data/col_hc_2234_1008.pkl', 'nextval')

#10/10
anal.receive_entire_sensors(datetime(2015,10,9,19,30), datetime(2015,10,10,7,40), 'data/col_cs_2112_1009.pkl', 'nextval')
anal.store_zone_sensors('RM-4134', datetime(2015,10,9,19,20), datetime(2015,10,10,1,20), 'nextval', 'data/dep_cc_4134_1009.pkl')
anal.store_zone_sensors('RM-4138', datetime(2015,10,9,19,20), datetime(2015,10,10,1,20), 'nextval', 'data/dep_cc_4138_1009.pkl')
anal.store_zone_sensors('RM-4214', datetime(2015,10,9,19,20), datetime(2015,10,10,1,20), 'nextval', 'data/dep_hc_4114_1009.pkl')
anal.store_zone_sensors('RM-4220', datetime(2015,10,9,19,20), datetime(2015,10,10,1,20), 'nextval', 'data/dep_hc_4220_1009.pkl')

#10/11
anal.store_zone_sensors('RM-3221', datetime(2015,10,10,23,12),datetime(2015,10,11,4,30), 'nextval', 'data/revdep_asfsp_3221_1010.pkl')
anal.store_zone_sensors('RM-3122', datetime(2015,10,10,23,12),datetime(2015,10,11,4,30), 'nextval', 'data/revdep_dc_3122_1010.pkl')
anal.receive_entire_sensors(datetime(2015,10,10,20,40), datetime(2015,10,11,8,40), 'data/col_cs_2112_1010.pkl', 'nextval')
anal.receive_entire_sensors(datetime(2015,10,10,21), datetime(2015,10,11,2,20), 'data/col_os_4208_1010.pkl', 'nextval')
anal.store_zone_sensors('RM-3256', datetime(2015,10,10,18,10),datetime(2015,10,11,8,30), 'nextval', 'data/reg_cs_3256_1010.pkl')
anal.store_zone_sensors('RM-4144', datetime(2015,10,10,23,50),datetime(2015,10,11,8,50), 'nextval', 'data/reg_cs_4144_1010.pkl')
anal.store_zone_sensors('RM-4148', datetime(2015,10,10,23,50),datetime(2015,10,11,8,50), 'nextval', 'data/reg_cs_4148_1010.pkl')
