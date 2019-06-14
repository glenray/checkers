from board import Board
from engines.littleBit import player as player
from engines.moron import player as moron
import numpy as np

brd = Board()
lb = player(brd)
moron = player(brd)

lb.rp = np.uint32(int('10001100000000010000100001000000', 2))
lb.bp = np.uint32(int('00000000000001000000010000011000', 2))
lb.k  = np.uint32(int('00000000000001000000000001000000', 2))
lb.emptySqs = ~(lb.rp | lb.bp )
brd.onMove = -1

lb.printBoard()
lb.printBoard( lb.getMovers() )

print('Red\t', lb.prBinary(lb.rp))
print('Black\t', lb.prBinary(lb.bp))
print('Kings\t', lb.prBinary(lb.k))
print('Empty\t', lb.prBinary(lb.emptySqs))
print('Empty2\t', ~(lb.rp | lb.bp ))