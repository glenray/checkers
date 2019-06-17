'''
Run tournament between 2 engines
'''
import sys
import importlib
from board import Board as board

if len( sys.argv ) > 1:
	rpName = sys.argv[1]
	bpName = sys.argv[2]
else:
	bpName = 'moron'
	rpName = 'littleBit'

b = board()
bp = getattr(importlib.import_module("engines."+bpName), 'player')(b)
rp = getattr(importlib.import_module("engines."+rpName), 'player')(b)

i = 1			# number of games to play
a = 0			# counter
red = 0			# red win count
black = 0		# black win count

while a < i: 
	# Play the game until no legal moves left
	moveNo = 1
	b.getLegalMoves()
	while b.legalMoves:
		# switch player
		player = bp if b.onMove == 1 else rp
		move = player.selectMove()
		moveNo +=1
		b.makeMove(move)

	# update game and win counters
	if (b.onMove==1):
		red +=1
		winner = rp.name
	else:
		black += 1
		winner = bp.name
	print('Game ',a, ' won by ',winner)
	a += 1
	
	# start the next game
	b.reset()

# print final tournament results
print("\nTournament Results")
print(f"{rp.name} as Red: {red}")
print(f"{bp.name} as Black: {black}")
