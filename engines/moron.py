import random

'''
Moron: The world's dumbest checkers bot. 
Returns randomly selected move 
Glen Pritchard -- 6/17/2018
'''
class player():
	def __init__(self, board):
		self.board = board
		self.name = "Moron"
		self.desc = "The world's dumbest checkers bot. Picks moves at random"

	def selectMove(self):
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moveList[moveNo]

	def __repr__(self):
		return "%s: %s" % (self.name, self.desc)