import sys
import pdb
import find_control
reload(find_control)
from find_control import FindControl

finder = FindControl()

if len(sys.argv)>1:
	if sys.argv[1]=='1':
		pdb.run("finder.top_part_reg()")
	else:
		finder.top_part_reg()
else:
	finder.top_part_reg()
