import copy
import random

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
		self.reached_max_depth = False
		self.depthcount = {}

	@property
	def name(self):
		return self._name

	@property
	def desc(self):
		return self._desc
	
	def selectMove(self, position=None, moves=None):
		value, move = self.max_value(self.board, 0, 3)
		if move:
			return move

	def max_value(self, upper_board, depth, maxdepth):
		'''
		Find minmax's best move at this depth of the search tree
		'''
		self.depthcount[depth] = self.depthcount.get(depth, 0) + 1
		v = float("-inf")
		board = copy.deepcopy(upper_board)
		board.getLegalMoves()
		if depth == maxdepth:
			# never used with even maxdepth.
			# print("max_value gets valuation")
			self.reached_max_depth = True
			return -self.pieceCount(board), None
		elif len(board.legalMoves) == 0:
			# minmax loses this branch
			return -100, None
		else:
			# iterate legal moves
			for move in board.legalMoves2FEN():
				# the problem is that this move is not unmade when the 
				# loop continues
				tempBoard = copy.deepcopy(board)
				tempBoard.makeMove(move)
				vtemp = v
				v = max(v, self.min_value(tempBoard, depth+1, maxdepth))
				if v > vtemp:
					best_move = move
				# attempts to solve the rock back and forth problem
				# but it seems to make minmax much dumber??
				# if v == vtemp:
					# best_move = random.choice((best_move, move))
			return v, best_move


	def min_value(self, upper_board, depth, maxdepth):
		'''
		Find the opponent's best move at this depth of the search tree
		'''
		self.depthcount[depth] = self.depthcount.get(depth, 0) + 1
		v = float("inf")
		board = copy.deepcopy(upper_board)
		board.getLegalMoves()
		if depth == maxdepth:
			self.reached_max_depth = True
			return self.pieceCount(board)
		elif len(board.legalMoves) == 0:
			# opponent loses in this branch
			return -100
		else:
			for move in board.legalMoves2FEN():
				# the problem is that this move is not unmade when the loop
				# continues
				tempBoard = copy.deepcopy(board)
				tempBoard.makeMove(move)
				vtemp, placeholder = self.max_value(tempBoard, depth+1, maxdepth)
				v = min(v, vtemp)
			return v

	def pieceCount(self, board = None):
		pos = self.board.position if board == None else board.position
		wp = pos.count(self.board.WP)
		wk = pos.count(self.board.WK)
		bp = pos.count(self.board.BP)
		bk = pos.count(self.board.BK)
		score = (bp + (bk*2)) - (wp + (wk*2))
		return -score if board.onMove == 1 else score

if __name__ == '__main__':
	pos = '[FEN "B:W18,26,27,25,11,19:BK15"]'
	p = player(Board(pos))
	p.board.printBoard()
	print(p.pieceCount())
