from board2 import Board
from engines.engine import Engine

'''
MinmaxA: First attempt at min max evaluation
Glen Pritchard -- 8/7/2022
'''
class player(Engine):
	def __init__(self, board):
		super(player, self).__init__( board )
		self._name = "MinMaxA"
		self._desc = "First attempt at minmax evaluation"
		self.board = board

	@property
	def name(self):
		return self._name

	@property
	def desc(self):
		return self._desc
	
	def selectMove(self, position=None, moves=None):
		pass

	def pieceCount(self):
		pos = self.board.position
		wp = pos.count(self.board.WP)
		wk = pos.count(self.board.WK)
		bp = pos.count(self.board.BP)
		bk = pos.count(self.board.BK)
		return wp + (wk*2), bp + (bk*2)

if __name__ == '__main__':
	pos = '[FEN "B:W18,26,27,25,11,19:BK15"]'
	p = player(Board())
	p.board.printBoard()
	print(p.pieceCount())
