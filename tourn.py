'''
Run tournament between 2 engines
'''
from board import Board as board
from engines.moron import player as moron
from engines.snap import player as snap

b = board()
bp = moron(b)
rp = moron(b)
i = 10		# number of games to play
a = 0			# counter
red = 0			# red win count
black = 0		# black win count

while a < i: 
	player = bp if b.onMove == 1 else rp
	while b.legalMoves:
		move = player.selectMove()
		b.makeMove(move)
	a += 1
	if (b.onMove==1):
		red +=1
	else:
		black += 1
	b.reset()
	b.getLegalMoves()

print(f"Red: {red}")
print(f"Black: {black}")
