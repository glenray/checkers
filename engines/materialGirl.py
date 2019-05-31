import random

'''
Material Girl: Select best move based on material after move 
First attempt to pick a good move
Glen Pritchard -- 5/31/2018
'''
class player():
	def __init__(self, board):
		self.board = board
		self.name = "Material Girl"
		self.desc = "Just don't lose material."

	def selectMove(self):
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		strPos = self.board.position

		print(self.board.onMove)
		for move in moveList:
			print(move)

		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moveList[moveNo]

	def __repr__(self):
		return "%s: %s" % (self.name, self.desc)