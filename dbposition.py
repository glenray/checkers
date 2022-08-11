from board2 import Board
import engines

def debug(pos, board, engines):
	board.printBoard()
	for engine in engines:
		move, score = engine.selectMove()
		print(f"{engine.name}@ d={engine.depth} - Move: {move}; Score: {score}")

'''
in this position, minmax5 moved from 14 to 18, ensuring a capture without compensation. That should not happen.
'''
pos = '[FEN "B:W17,21,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,10,11,12,14"]'
b = Board(pos)
debug(pos, b, [engines.minmaxA(b, depth=5)])