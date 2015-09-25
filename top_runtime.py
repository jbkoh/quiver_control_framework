from runtime import Runtime
import sys
import pdb

runt = Runtime()
runt.top(sys.argv[1])

#if sys.argv[1] == '1':
#	pdb.run("runt.top('commands/test.xlsx')")
#else:
#	runt.top('commands/test.xlsx')
