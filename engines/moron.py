'''
Moron: The world's dumbest checkers bot. 
Returns randomly selected move 
Glen Pritchard -- 6/17/2018
'''
import random
from engines.engine import Engine

class player( Engine ):
	def __init__(self, board):
		super(player, self).__init__( board )
		self._name = "Moron"
		self._desc = "The world's dumbest checkers bot. Picks moves at random"

	@property
	def name(self):
		return self._name

	@property
	def desc(self):
		return self._desc
	
	def selectMove(self, position, moves):
		moveLen = len(moves)
		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moves[moveNo]