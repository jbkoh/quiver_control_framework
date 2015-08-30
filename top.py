import runtime
reload(runtime)
from runtime import Runtime
import sys
import pdb
from datetime import datetime

runmodule = Runtime()

commIn= runmodule.read_seq('commands/test.xlsx')
runmodule.store_seq(commIn)

seqDf = runmodule.load_seq(datetime(2015,8,21,0,0,0),datetime(2015,8,30,0,0,0))
print seqDf

#runmodule.read
#runmodule.load
#runmodule.validate_command_seq
#runmodule.store()
