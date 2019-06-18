'''
Run tournament between 2 engines
'''
import sys
import importlib
from board import Board as board
from debug import debug
from engines.littleBit import player as lb

if len( sys.argv ) > 1:
	bpName = sys.argv[1]
	rpName = sys.argv[2]
else:
	bpName = 'moron'
	rpName = 'snap'

b = board()
bit = lb(b)
db = debug()
bp = getattr(importlib.import_module("engines."+bpName), 'player')(b)
rp = getattr(importlib.import_module("engines."+rpName), 'player')(b)

i = 100			# number of games to play
a = 1			# counter
red = 0			# red win count
black = 0		# black win count
draw = 0		# draw count
mostMoves = 0

while a <= i: 
	# Play the game until no legal moves left
	isdraw = False
	moveNo = 1
	b.getLegalMoves()
	while b.legalMoves and isdraw == False:
		# select player on move
		player = bp if b.onMove == 1 else rp
		move = player.selectMove()
		moveNo +=1
		if moveNo == 1000:
			isdraw = True
		b.makeMove(move)

	# update counters; print game message
	if isdraw == True:
		draw += 1
		message = "Draw"
	elif (b.onMove==1):
		red +=1
		message = f'Game {a} won by {rp.name} in {moveNo} moves.'
	else:
		black += 1
		message = f'Game {a} won by {bp.name} in {moveNo} moves.'
	print(message)
	
	a += 1
	if moveNo > mostMoves and isdraw == False:
		mostMoves = moveNo
	
	# start the next game
	b.reset()

# print final tournament results
print("\nTournament Results")
print(f"{bp.name} as Black: {black}")
print(f"{rp.name} as Red: {red}")
print(f"Draws: {draw}")
print(f"Most Moves (when game not a draw): {mostMoves}")
