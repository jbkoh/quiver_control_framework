import sys
import pdb
from find_control import FindControl

finder = FindControl()

if len(sys.argv)>1:
	if sys.argv[1]=='1':
		pdb.run("finder.organize_data()")
	else:
		finder.organize_data()
