import timeit

import copy
from board2 import Board
from positions import positions

b = Board(positions["royalTour"])
p = b.position

def statusQuo():
	board = copy.deepcopy(b)
	board.getLegalMoves()
	moves = board.legalMoves2FEN()
	board.makeMove(moves[0])

def change():
	pos = copy.copy(p)
	b.position = pos
	moves = b.legalMoves2FEN()
	b.makeMove(moves[0])

def idea():
	board = Board(positions["royalTour"])
	board.getLegalMoves()
	moves = board.legalMoves2FEN()
	board.makeMove(moves[0])

# print(timeit.timeit(lambda:statusQuo(), number=100000))
print(timeit.timeit(lambda:change(), number=100000))
# print(timeit.timeit(lambda:idea(), number=100000))
