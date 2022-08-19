import copy
import random
import time

from board2 import Board
from engines.engine import Engine
from engines.moveNode import moveNode

'''
MinmaxB: Enhance MinmaxA to improve speed
MinmaxA deep copied the board2.Board instance for each
node in the move tree.
MinmanB copies only the board2.Board.position and board2.Board.onMove.
This results in approx 5x increase in speed over MinmaxA.
MinmaxB produces the same move tree as MinmaxA.
Roughly, MinmaxB can probe one level deeper than MinmaxA in the same amount of time.
Glen Pritchard -- 8/15/2022
'''
class player(Engine):
	'''
	@param board obj: instance of board2.Board
	@param maxdepth int: maximum depth of move tree
	@param ab bool: Flag to use alpha beta pruning
	@param maketree bool: True to create entire move tree in self.root
	'''
	def __init__(self, board, maxdepth=3, ab=False, maketree=False):
		super(player, self).__init__( board )
		self._name = "MinMaxB"
		self._desc = "A faster MinMaxA"
		self.board = board
		self.maxdepth = maxdepth
		self.maketree = maketree
		self.ab = ab
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
		self.totalNodes = 0
		startTime = time.time()
		self.root = moveNode(copy.deepcopy(self.board)) if self.maketree else None
		pos = (copy.copy(self.board.position), self.board.onMove)
		value, move = self.max_value(pos, 0, float("-inf"), float("inf"), self.root)
		endTime = time.time()
		self.elapsedTime = round(endTime - startTime, 2)
		try:
			self.nps = int(self.totalNodes/self.elapsedTime)
		except ZeroDivisionError:
			self.nps = "0 Error"
		self.score = value
		return move

	def max_value(self, upper_pos, depth, alpha, beta, parentNode=None):
		'''
		Find minmax's best move at depth of the search tree
		@param upper_board obj Board: a Board object
		@param depth int: the current depth in the search tree
		@param parentNode obj moveNode: a
		'''
		self.setScratchBoard(upper_pos)
		self.scratchBoard.getLegalMoves()
		v = float("-inf")
		# Return the position's score at if at maxdepth
		if depth == self.maxdepth:
			return self.pieceCount(self.scratchBoard), None
		# if there no legal moves, minmax loses the game in this branch
		elif len(self.scratchBoard.legalMoves) == 0:
			return -100, None
		# iterate legal moves and call the next node level
		else:
			for move in self.scratchBoard.legalMoves2FEN():
				self.setScratchBoard(upper_pos)
				self.scratchBoard.makeMove(move)
				vtemp = v
				if parentNode:
					node = moveNode(copy.deepcopy(self.scratchBoard))
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes +=1
				v = max(v, self.min_value(
					(copy.copy(self.scratchBoard.position), self.scratchBoard.onMove), 
					depth+1, 
					alpha,
					beta,
					node))
				if v > vtemp:
					best_move = move
				# pruning
				if self.ab:
					if v >= beta:
						return v, best_move
					alpha = max(alpha, v)
				if parentNode:
					node.v = self.pieceCount(self.scratchBoard)
					node.move = move
			return v, best_move

	def min_value(self, upper_pos, depth, alpha, beta, parentNode=None):
		'''
		Find the opponent's best move at this depth of the search tree
		'''
		self.setScratchBoard(upper_pos)
		self.scratchBoard.getLegalMoves()
		v = float("inf")
		if depth == self.maxdepth:
			return self.pieceCount(self.scratchBoard)
		elif len(self.scratchBoard.legalMoves) == 0:
			# opponent loses in this branch
			return 100
		else:
			for move in self.scratchBoard.legalMoves2FEN():
				self.setScratchBoard(upper_pos)
				self.scratchBoard.makeMove(move)
				if parentNode:
					node = moveNode(copy.deepcopy(self.scratchBoard))
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes +=1
				vtemp, placeholder = self.max_value(
					(copy.copy(self.scratchBoard.position), self.scratchBoard.onMove), 
					depth+1, 
					alpha,
					beta, 
					node)
				v = min(v, vtemp)
				if self.ab:
					if v <= alpha:
						return v
					beta = min(beta, v)
				if parentNode:
					node.move = move
					node.v = self.pieceCount(self.scratchBoard)
			return v

	def setScratchBoard(self, pos):
		self.scratchBoard.position = copy.copy(pos[0])
		self.scratchBoard.onMove = pos[1]

	def pieceCount(self, board = None):
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
	b = Board(pos)
	p = player(b, maxdepth=8, ab=True)
	move = p.selectMove()
	p.board.makeMove(move)
	print(b.printBoard())
	print(f"{p.name} moves {move}, Score: {p.score}, \nTime: {p.elapsedTime}; nodes: {p.totalNodes}; nps: {p.nps}")
