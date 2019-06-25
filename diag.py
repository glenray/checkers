from board import Board
from engines.littleBit import player as littlebit
from engines.moron import player as moron
from engines.snap import player as snap
import numpy as np
import operator
from debug import debug


brd = Board('[FEN "B:W26,27,25,11K:B15K,14K"]')
lb = littlebit(brd)
db = debug()

lb.convert2BB()
brd.onMove = 1

print( db.template )
print( db.printBoard( lb ) )
print( db.printBoard( lb, lb.getJumpers() ) )

print(db.bitHead,'\n')
print(db.prBinary(lb.bp), 'Black')
print(db.prBinary(lb.rp), 'Red')
print(db.prBinary(lb.k), 'Kings')
print(db.prBinary(lb.emptySqs), 'Empty')
print(db.prBinary(lb.getMovers()), 'Movers')
print(db.prBinary(lb.getJumpers()), 'Jumpers')