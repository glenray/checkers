from board import Board
from engines.littleBit import player as player
from engines.moron import player as moron
import numpy as np
import operator


brd = Board()
lb = player(brd)
moron = player(brd)

lb.rp = np.uint32(0b10001100000000010000100001000000)
lb.bp = np.uint32(0b00000000000001000000010000011000)
lb.k  = np.uint32(0b00000000000001000000000001000000)
lb.emptySqs = ~(lb.rp | lb.bp )
brd.onMove = -1
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
print(lb.printBoard())
print(lb.printBoard( lb.getMovers() ))

print('\t\t\t 33222222222211111111110000000000')
print('\t\t\t 10987654321098765432109876543210\n')
print('Red\t\t', lb.prBinary(lb.rp))
print('Black\t', lb.prBinary(lb.bp))
print('Kings\t', lb.prBinary(lb.k))
print('Empty\t', lb.prBinary(lb.emptySqs))
print('SEmp\t', lb.prBinary(lb.emptySqs << 4  & lb.rp ))
print('SEmp\t', lb.prBinary(operator.lshift( lb.emptySqs, 4)  & lb.rp ))
print('Mover\t', lb.prBinary(lb.getMovers()))
# print('L5\t\t', lb.prBinary(lb.MASK_L5))
# print('L3\t\t', lb.prBinary(lb.MASK_L3))
# print('R3\t\t', lb.prBinary(lb.MASK_R3))
# print('R5\t\t', lb.prBinary(lb.MASK_R5))
