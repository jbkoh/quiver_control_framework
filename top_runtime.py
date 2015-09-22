from runtime import Runtime
import sys
import pdb

runt = Runtime()

if sys.argv[1] == '1':
	pdb.run("runt.top('commands/test.xlsx')")
else:
	runt.top('commands\lab_0921_4.xlsx')
