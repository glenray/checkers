'''
Snap: Always plays the first move on the list. 
Glen Pritchard -- 6/29/2018
'''
from engines.engine import Engine
import time

class player( Engine ):
	def __init__(self, board):
		super(player, self).__init__(board)
		self._name = "Snap"
		self._desc = "Picks the first move on the list"

	def selectMove(self):
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		if moveLen > 0:
			return moveList[0]

	@property
	def name(self):
		return self._name

	@property
	def desc(self):
		return self._desc