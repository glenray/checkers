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
	rpName = 'moron'
	bpName = 'moron'

b = board()
bp = getattr(importlib.import_module("engines."+bpName), 'player')(b)
rp = getattr(importlib.import_module("engines."+rpName), 'player')(b)

i = 100			# number of games to play
a = 0			# counter
red = 0			# red win count
black = 0		# black win count

while a < i: 
	# Play the game until no legal moves left
	moveNo = 1
	while b.legalMoves:
		# switch player
		player = bp if b.onMove == 1 else rp
		move = player.selectMove()
		print(a,move,player.name,moveNo)
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
	b.getLegalMoves()

# print final tournament results
print("\nTournament Results")
print(f"{rp.name} as Red: {red}")
print(f"{bp.name} as Black: {black}")
