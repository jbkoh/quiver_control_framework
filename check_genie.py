from bd_wrapper import BDWrapper
from analyzer import Analyzer
from datetime import datetime, timedelta
import csv

anal = Analyzer()

zonelist = ['RM-3232',\
'RM-2138',\
'RM-2134',\
'RM-2230',\
'RM-3138',\
'RM-1200B',\
'RM-B250',\
'RM-4126',\
'RM-1108',\
'RM-2150',\
'RM-1102',\
'RM-3254',\
'RM-3148',\
'RM-3142',\
'RM-3140',\
'RM-B260',\
'RM-4114',\
'RM-2140',\
'RM-1212',\
'RM-2262',\
'RM-3150',\
'RM-3152',\
'RM-4102',\
'RM-B275',\
'RM-3260',\
'RM-2142',\
'RM-2226',\
'RM-4236',\
'RM-B215',\
'RM-B215',\
'RM-3217',\
'RM-2217',\
'RM-2109',\
'RM-2102',\
'RM-4140',\
'RM-4148'
]
filteredZoneList = list()

for zone in zonelist:
	ocData = anal.receive_a_sensor(zone, 'Occupied Command', datetime(2015,10,12,22,00), datetime(2015,10,13,1,0), 'nextval')
	if 1 in ocData.tolist():
		filteredZoneList.append(zone)	

print filteredZoneList
myfile = open('result/geniecontrolled_zones.csv', 'wb')
wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
wr.writerow(filteredZoneList)
