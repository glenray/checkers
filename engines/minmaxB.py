import copy
import random

from board2 import Board
from engines.engine import Engine

'''
MinmaxB: Enhance MinmaxA to improve speed
Glen Pritchard -- 8/15/2022
'''
class player(Engine):
	'''
	@param board obj: instance of board2.Board
	@param maxdepth int: maximum depth of move tree
	@param maketree bool: True to create entire move tree in self.tree
	'''
	def __init__(self, board, maxdepth = 3, maketree = False):
		super(player, self).__init__( board )
		self._name = "MinMaxB"
		self._desc = "A faster MinMaxA"
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
		self.root = moveNode(self.board) if self.maketree else None
		value, move = self.max_value(self.board, 0, self.maxdepth, self.root)
		self.score = value
		return move

	def max_value(self, upper_board, depth, maxdepth, parentNode=None):
		'''
		Find minmax's best move at this depth of the search tree
		@param upper_board obj Board: a Board object
		@param depth int: the current depth in the search tree
		@param maxdepth int: the maximum depth of the search tree
		@param parentNode obj moveNode: a
		'''
		v = float("-inf")
		board = copy.deepcopy(upper_board)
		board.getLegalMoves()
		# Return the position's score at if at maxdepth
		if depth == maxdepth:
			return self.pieceCount(board), None
		# if there no legal moves, minmax loses the game in this branc
		elif len(board.legalMoves) == 0:
			# breakpoint()
			return -100, None
		# iterate legal moves and call the next node level
		else:
			for move in board.legalMoves2FEN():
				tempBoard = copy.deepcopy(board)
				tempBoard.makeMove(move)
				vtemp = v
				if parentNode:
					node = moveNode(tempBoard)
					parentNode.addChild(node)
				else:
					node = None
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

class moveNode:
	def __init__(self, board, parent = None):
		self.board = board
		self.parent = parent
		self.children = []

	def addChild(self, child):
		self.children.append(child)
		child.parent = self

	def printChildren(self):
		for i, child in enumerate(self.children):
			print(i)
			print(child.__repr__())

	def getRootNode(self):
		''' Returns tree root node '''
		if self.parent == None:
			return self
		x = self.parent
		while True:
			if x.parent == None:
				return x
			else:
				x = x.parent

	def countNodes(self):
		''' Return count of this nodes children and all decendents '''
		return self._countChildren() + len(self.children)

	def _countChildren(self):
		''' 
		Return the count of all child nodes under the current node
		This does not include the child nodes within the current node
		'''
		n = 0
		for child in self.children:
			n+=len(child.children)
			n+=child._countChildren()
		return n

	def getLeafNodes(self):
		'''
		@return: list: list of nodes from bottom of tree, i.e.,
			those no children
		'''
		result = []
		for child in self.children:
			if child.children:
				result += child.getLeafNodes()
			else:
				result.append(child)
		return result


	def __repr__(self):
		return self.board.printBoard()

if __name__ == '__main__':
	pos = '[FEN "B:W18,26,27,25,11,19:BK15"]'
	p = player(Board(), maxdepth=5)
	p.selectMove()
