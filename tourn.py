'''
Run tournament between 2 engines
'''
import sys
import importlib
from board import Board as board
from engines.moron import player as moron
# from engines.snap import player as snap


b = board()

bp = getattr(importlib.import_module("engines.snap"), 'player')(b)
rp = getattr(importlib.import_module("engines.moron"), 'player')(b)

i = 10			# number of games to play
a = 0			# counter
red = 0			# red win count
black = 0		# black win count

while a < i: 
	print('Game ',a)
	while b.legalMoves:
		player = bp if b.onMove == 1 else rp
		move = player.selectMove()
		b.makeMove(move)

	a += 1
	if (b.onMove==1):
		red +=1
	else:
		black += 1
	
	b.reset()
	b.getLegalMoves()

print(f"{rp.name} as Red: {red}")
print(f"{bp.name} as Black: {black}")
