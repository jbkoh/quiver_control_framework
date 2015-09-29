from determine_control import DetermineControl
import pdb
import sys


deter = DetermineControl()
df = deter.make_dataframe('data/2015-09-28T1.pkl')

if sys.argv[1] =='1':
	pdb.run("deter.make_most_influence_dict(df['RM-4132'])")
else:
	deter.make_most_influence_dict(df['RM-4132'])
