from board import Board
from engines.littleBit import player as player
from engines.moron import player as moron
import numpy as np
import operator
from debug import debug

brd = Board('[FEN "B:W18,26,27,25,11,19:B15K"]')
lb = player(brd)
moron = player(brd)
db = debug()

lb.convert2BB()
brd.onMove = 1
template = """  00  01  02  03
04  05  06  07
  08  09  10  11
12  13  14  15
  16  17  18  19
20  21  22  23
  24  25  26  27
28  29  30  31
"""

print( template )
print( db.printBoard( lb ) )
print( db.printBoard( lb, lb.getMovers() ) )

print('\t\t\t 33222222222211111111110000000000')
print('\t\t\t 10987654321098765432109876543210\n')
print('Red\t\t', db.prBinary(lb.rp))
print('Black\t', db.prBinary(lb.bp))
print('Kings\t', db.prBinary(lb.k))
print('Empty\t', db.prBinary(lb.emptySqs))
print('Mover\t', db.prBinary(lb.getMovers()))
