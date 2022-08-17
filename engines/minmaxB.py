import copy
import random
import time

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
		self.scratchBoard = copy.deepcopy(self.board)

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
		startTime = time.time()
		self.root = moveNode(self.board) if self.maketree else None
		pos = (copy.copy(self.board.position), self.board.onMove)
		value, move = self.max_value(
			pos, 
			0, 
			self.maxdepth, 
			self.root)
		endTime = time.time()
		self.elapsedTime = endTime - startTime
		if self.elapsedTime == 0:
			self.nps = "Divide by Zero"
		else:
			self.nps = self.totalNodes/self.elapsedTime
		self.score = value
		return move

	def max_value(self, upper_pos, depth, maxdepth, parentNode=None):
		'''
		Find minmax's best move at depth of the search tree
		@param upper_board obj Board: a Board object
		@param depth int: the current depth in the search tree
		@param maxdepth int: the maximum depth of the search tree
		@param parentNode obj moveNode: a
		'''
		v = float("-inf")
		self.setScratchBoard(upper_pos)
		self.scratchBoard.getLegalMoves()
		
		# Return the position's score at if at maxdepth
		if depth == maxdepth:
			return self.pieceCount(self.scratchBoard), None
		# if there no legal moves, minmax loses the game in this branch
		elif len(self.scratchBoard.legalMoves) == 0:
			return -100, None
		# iterate legal moves and call the next node level
		else:
			for move in self.scratchBoard.legalMoves2FEN():
				# remember the current position
				tempPos = upper_pos
				self.scratchBoard.makeMove(move)
				vtemp = v
				if parentNode:
					node = moveNode(tempBoard)
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes +=1
				v = max(v, self.min_value(
					(copy.copy(self.scratchBoard.position), self.scratchBoard.onMove), 
					depth+1, 
					maxdepth, 
					node))
				if v > vtemp:
					best_move = move
				if parentNode:
					node.v = self.pieceCount(tempBoard)
					node.move = move
				# return scratch board to original state for next legal move iteration
				self.setScratchBoard(tempPos)
			return v, best_move

	def min_value(self, upper_pos, depth, maxdepth, parentNode=None):
		'''
		Find the opponent's best move at this depth of the search tree
		'''
		v = float("inf")
		self.setScratchBoard(upper_pos)
		self.scratchBoard.getLegalMoves()
		if depth == maxdepth:
			return self.pieceCount(self.scratchBoard)
		elif len(self.scratchBoard.legalMoves) == 0:
			# opponent loses in this branch
			# breakpoint()
			return 100
		else:
			for move in self.scratchBoard.legalMoves2FEN():
				# Save the current position
				tempPos = upper_pos
				self.scratchBoard.makeMove(move)
				if parentNode:
					node = moveNode(tempBoard)
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes +=1
				vtemp, placeholder = self.max_value(
					(copy.copy(self.scratchBoard.position), self.scratchBoard.onMove), 
					depth+1, 
					maxdepth, 
					node)
				v = min(v, vtemp)
				if parentNode:
					node.move = move
					node.v = self.pieceCount(tempBoard)
				# return scratch board to original state for next move
				self.setScratchBoard(tempPos)
			return v

	def setScratchBoard(self, pos):
		self.scratchBoard.position = pos[0]
		self.scratchBoard.onMove = pos[1]

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
	b = Board()
	p = player(b, maxdepth=7)
	move = p.selectMove()
	p.board.makeMove(move)
	print(b.printBoard())
	print(f"{p.name} moves {move}, Score: {p.score}, \nTime: {p.elapsedTime}; nodes: {p.totalNodes}; nps: {p.nps}")
