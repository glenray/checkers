'''
Snap: Always plays the first move on the list. 
Glen Pritchard -- 6/29/2018
'''
from engines.engine import Engine

class player( Engine ):
	@property
	def name(self):
		return "Snap"

	@property
	def desc(self):
		return "Picks the first move on the list"

	def selectMove(self):
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		if moveLen > 0:
			return moveList[0]