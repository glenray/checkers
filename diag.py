from board import Board
from engines.littleBit import player as player
from engines.moron import player as moron

brd = Board()
lb = player(brd)
moron = player(brd)


lb.rp = 0b11111111101101000000000000000000
lb.bp = 0b00000000000000000110100111111111
lb.k  = 0b00000000000000000000000000000000

brd.onMove = 1
brd.getLegalMoves()

lb.printBoard()
print(lb.getMovers())