from quiver import Quiver
import pdb
import sys

quiv = Quiver()

if len(sys.argv)>=1:
	if sys.argv[1]=='1':
		pdb.run("quiv.emergent_rollback()")
	else:
		quiv.emergent_rollback()
else:
	quiv.emergent_rollback()

