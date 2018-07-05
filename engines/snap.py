'''
Snap: Always plays the first move on the list. 
Glen Pritchard -- 6/29/2018
'''
class player():
	def __init__(self, board):
		self.board = board
		self.name = "Snap"
		self.desc = "Picks the first move on the list."

	def selectMove(self):
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		return moveList[0]

	def __repr__(self):
		return "%s: %s" % (self.name, self.desc)