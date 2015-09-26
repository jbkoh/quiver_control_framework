from analyzer import Analyzer
from collection_wrapper import *

logColl = ColletionWrapper('experience_log')
anal = Analyzer()
logColl.to_csv()
timeFormat = '%Y%m%dT%H%M%S'
beginTime = datetime.strptime(sys.argv[1], timeFormat)
endTime = datetime.strptime(sys.argv[2], timeFormat)

anal.receive_entire_sensors(beginTime, endTime)
