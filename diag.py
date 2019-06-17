from board import Board
from engines.littleBit import player as littlebit
from engines.moron import player as moron
from engines.snap import player as snap
import numpy as np
import operator
from debug import debug


brd = Board('[FEN "B:W18,26,27,25,11,19:B15K"]')
x = littlebit(brd)
print(x.board)
exit()

lb = littlebit(brd)
moron = littlebit(brd)
db = debug()

lb.convert2BB()
brd.onMove = -1

print( db.template )
print( db.printBoard( lb ) )
print( db.printBoard( lb, lb.getMovers() ) )

print(db.bitHead,'\n')
print(db.prBinary(lb.bp), 'Black')
print(db.prBinary(lb.rp), 'Red')
print(db.prBinary(lb.k), 'Kings')
print(db.prBinary(lb.emptySqs), 'Empty')
print(db.prBinary(lb.getMovers()), 'Movers')
