import sys
import pdb
import find_control
reload(find_control)
from find_control import FindControl

finder = FindControl()

if len(sys.argv)>1:
	if sys.argv[1]=='1':
		pdb.run("finder.all_relationship()")
	else:
		finder.all_relationship()
else:
	finder.all_relationship()