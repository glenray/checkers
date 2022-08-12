import copy
import random

from board2 import Board
from engines.engine import Engine

'''
MinmaxA: First attempt at min max evaluation
Glen Pritchard -- 8/7/2022
'''
class player(Engine):
	def __init__(self, board, maxdepth = 3):
		super(player, self).__init__( board )
		self._name = "MinMaxA"
		self._desc = "First attempt at minmax evaluation"
		self.board = board
		self.maxdepth = maxdepth

	@property
	def name(self):
		return f"{self._name}@d{self.maxdepth}"

	@name.setter
	def name(self, newname):
		self._name = newname

	@property
	def desc(self):
		return self._desc
	
	def selectMove(self, position=None, moves=None):
		root = moveNode(self.board)
		value, move = self.max_value(self.board, 0, self.maxdepth, root)
		breakpoint()
		return move, value

	def max_value(self, upper_board, depth, maxdepth, parentNode=None):
		'''
		Find minmax's best move at this depth of the search tree
		'''
		v = float("-inf")
		board = copy.deepcopy(upper_board)
		board.getLegalMoves()
		if depth == maxdepth:
			return self.pieceCount(board), None
		elif len(board.legalMoves) == 0:
			# minmax loses this branch
			return -100, None
		else:
			# iterate legal moves
			for move in board.legalMoves2FEN():
				tempBoard = copy.deepcopy(board)
				tempBoard.makeMove(move)
				node = moveNode(tempBoard)
				parentNode.addChild(node)
				vtemp = v
				v = max(v, self.min_value(tempBoard, depth+1, maxdepth, node))
				if v > vtemp:
					best_move = move
				node.v = self.pieceCount(tempBoard)
				node.move = move

				# attempts to solve the rock back and forth problem
				# but it seems to make minmax much dumber??
				# if depth == 0 and v == vtemp:
				# 	best_move = random.choice((best_move, move))
			
			return v, best_move

	def min_value(self, upper_board, depth, maxdepth, parentNode):
		'''
		Find the opponent's best move at this depth of the search tree
		'''
		v = float("inf")
		board = copy.deepcopy(upper_board)
		board.getLegalMoves()
		if depth == maxdepth:
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
				node = moveNode(tempBoard)
				parentNode.addChild(node)
				vtemp, placeholder = self.max_value(tempBoard, depth+1, maxdepth, node)
				v = min(v, vtemp)
				node.move = move
				node.v = self.pieceCount(tempBoard)
			return v

	def pieceCount(self, board = None):
		# breakpoint()
		pos = self.board.position if board == None else board.position
		wp = pos.count(self.board.WP)
		wk = pos.count(self.board.WK)
		bp = pos.count(self.board.BP)
		bk = pos.count(self.board.BK)
		# we should evaluate the position from the perspective of the side to move
		blackScore = (bp + (bk*2)) - (wp + (wk*2))
		return blackScore if self.board.onMove == 1 else -blackScore 

class moveNode:
	def __init__(self, board, parent = None):
		self.board = board
		self.parent = parent
		self.children = []

	def addChild(self, child):
		self.children.append(child)
		child.parent = self

	def __repr__(self):
		return self.board.printBoard()

if __name__ == '__main__':
	pos = '[FEN "B:W18,26,27,25,11,19:BK15"]'
	p = player(Board(pos), maxdepth=5)
	p.selectMove()
