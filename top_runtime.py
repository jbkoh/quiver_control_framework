from runtime import Runtime
import sys
import pdb

runt = Runtime()

if sys.argv[1] == '1':
	pdb.run("runt.top()")
else:
	runt.top()