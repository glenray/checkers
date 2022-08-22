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
	@param ab bool: True to use alpha-beta pruning
	@param randomize bool: True to randomize the order of legal moves to avoid deterministic play
	@param maketree bool: True to create entire move tree in self.root
	'''
	def __init__(self, board, maxdepth=3, ab=False, randomize=True, maketree=False):
		super(player, self).__init__( board )
		self._name = "MinMaxB"
		self._desc = "A faster MinMaxA"
		self.board = board
		self.maxdepth = maxdepth
		self.randomize = randomize
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
		value, move = self.negaMax(pos, 0, float("-inf"), float("inf"), -1, self.root)
		endTime = time.time()
		self.elapsedTime = round(endTime - startTime, 2)
		try:
			self.nps = int(self.totalNodes/self.elapsedTime)
		except ZeroDivisionError:
			self.nps = "0 Error"
		self.score = value
		return move

	def negaMax(self, upper_pos, depth, alpha, beta, mp, parentNode=None):
		'''
		Find minmax's best move at depth of the search tree
		@param upper_board obj Board: a Board object
		@param depth int: the current depth in the search tree
		@param parentNode obj moveNode: a
		'''
		self.setScratchBoard(upper_pos)
		self.scratchBoard.getLegalMoves()
		# breakpoint()
		v = float("-inf")
		# Return the position's score at if at maxdepth
		if depth == self.maxdepth:
			return self.pieceCount(self.scratchBoard) * -mp, None
		# if there no legal moves, minmax loses the game in this branch
		elif len(self.scratchBoard.legalMoves) == 0:
			return 100 * mp, None
		# iterate legal moves and call the next node level
		else:
			for move in self.getFenMoveList():
				self.setScratchBoard(upper_pos)
				self.scratchBoard.makeMove(move)
				vtemp = v
				if parentNode:
					node = moveNode(copy.deepcopy(self.scratchBoard))
					parentNode.addChild(node)
				else:
					node = None
				self.totalNodes +=1
				vtemp, placeholder = self.negaMax(
					(copy.copy(self.scratchBoard.position), self.scratchBoard.onMove), 
					depth+1, 
					alpha,
					beta,
					-mp,
					node)
				if vtemp > v:
					best_move = move
				v = max(v, vtemp)

				# pruning
				if self.ab:
					if mp == -1:
						if v >= beta:
							return v, best_move
						alpha = max(alpha, v)
					else:
						if v <= alpha:
							return v, best_move
						beta = min(beta, v)

				# make tree
				if parentNode:
					node.v = self.pieceCount(self.scratchBoard)
					node.move = move
			return v, best_move

	def getFenMoveList(self):
		fenmoves = self.scratchBoard.legalMoves2FEN()
		if self.randomize:
			random.shuffle(fenmoves)
		return fenmoves

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
	p = player(b, maxdepth=2, ab=True, randomize = True)
	move = p.selectMove()
	p.board.makeMove(move)
	print(b.printBoard())
	print(f"{p.name} moves {move}, Score: {p.score}, \nTime: {p.elapsedTime}; nodes: {p.totalNodes}; nps: {p.nps}")
