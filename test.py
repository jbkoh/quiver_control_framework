from quiver import Quiver
from collection_wrapper import *
import pdb
from datetime import datetime

statColl = CollectionWrapper('status')
statRow1 = StatusRow('e7697d5a-77df-11e2-83c4-00163e005319', 'UCSD-Main-EBU3B-Flr-4-Rm-4132-Common Setpoint',datetime(2015,9,18,16,0), 73,72,'Common Setpoint', True)
statRow2 = StatusRow('e84fe38a-77df-11e2-83c4-00163e005319', 'UCSD-Main-EBU3B-Flr-4-Rm-4132-Occupied Clg Min',datetime(2015,9,18,14,0), 0,80,'Occupied Clg Min', True)
statColl.store_row(statRow1)
statColl.store_row(statRow2)

quiv = Quiver()
pdb.run("quiv.emergent_rollback()")
