from board import Board
from engines.littleBit import player as player
from engines.moron import player as moron

brd = Board()
lb = player(brd)
moron = player(brd)

lb.rp = int('11111111101101000000000000000000', 2)
lb.bp = int('00000000000000000110100111111111', 2)
lb.k  = int('00000000000000000000000000000000', 2)
brd.onMove = 1

lb.convert2BB()
print(lb.getMovers())