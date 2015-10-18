import sys
import pdb
import find_dep
reload(find_dep)
from find_dep import FindDep

finder = FindDep()

#if len(sys.argv)>1:
#	if sys.argv[1]=='1':
#		pdb.run("finder.dep_analysis()")
#	else:
#		pass
#else:
#		pass
#finder.dep_analysis()

if len(sys.argv)>1:
	if sys.argv[1]=='1':
		pdb.run("finder.dep_analysis_all()")
	else:
		pass
else:
		pass
finder.dep_analysis_all()
