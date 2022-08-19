import copy
import random
import time

from board2 import Board
from engines.engine import Engine
from engines.moveNode import moveNode

'''
MinmaxA: First attempt at minimax evaluation
Glen Pritchard -- 8/7/2022
'''
class player(Engine):
	def __init__(self, board, maxdepth=3, maketree=False):
		super(player, self).__init__(board)
		self._name = "MinMaxA"
		self._desc = "First attempt at minmax evaluation"
		self.board = board
		self.maxdepth = maxdepth
		self.maketree = maketree
		# if maketree is True, the root of the move tree will be stored here
		self.root = None

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
		self.totalNodes = 0
		startTime = time.time()
		self.root = moveNode(self.board) if self.maketree else None
		value, move = self.max_value(self.board, 0, self.maxdepth, self.root)
		endTime = time.time()
		self.elapsedTime = round(endTime - startTime, 2)
		try:
			self.nps = int(self.totalNodes/self.elapsedTime)
		except ZeroDivisionError:
			self.nps = "0 Error"
		self.score = value
		return move

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
			# breakpoint()
			return -100, None
		else:
			# iterate legal moves
			for move in board.legalMoves2FEN():
				tempBoard = copy.deepcopy(board)
				tempBoard.makeMove(move)
				vtemp = v
				if parentNode:
					node = moveNode(tempBoard)
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes += 1
				v = max(v, self.min_value(tempBoard, depth+1, maxdepth, node))
				if v > vtemp:
					best_move = move
				if parentNode:
					node.v = self.pieceCount(tempBoard)
					node.move = move

				# attempts to solve the rock back and forth problem
				# but it seems to make minmax much dumber??
				# if depth == 0 and v == vtemp:
				# 	best_move = random.choice((best_move, move))
			
			return v, best_move

	def min_value(self, upper_board, depth, maxdepth, parentNode=None):
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
			# breakpoint()
			return 100
		else:
			for move in board.legalMoves2FEN():
				# the problem is that this move is not unmade when the loop
				# continues
				tempBoard = copy.deepcopy(board)
				tempBoard.makeMove(move)
				if parentNode:
					node = moveNode(tempBoard)
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes +=1
				vtemp, placeholder = self.max_value(tempBoard, depth+1, maxdepth, node)
				v = min(v, vtemp)
				if parentNode:
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

if __name__ == '__main__':
	pos = '[FEN "B:W18,26,27,25,11,19:BK15"]'
	p = player(Board(), maxdepth=5)
	p.selectMove()
