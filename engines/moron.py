'''
Moron: The world's dumbest checkers bot. 
Returns randomly selected move 
Glen Pritchard -- 6/17/2018
'''
import random
from engines.engine import Engine

class player( Engine ):

	@property
	def name(self):
		return "Moron"

	@property
	def desc(self):
		return "The world's dumbest checkers bot. Picks moves at random"
	
	def selectMove(self):
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moveList[moveNo]