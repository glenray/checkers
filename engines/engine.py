from abc import ABC, abstractmethod, abstractproperty

class Engine(ABC):
	'''
	Abstract base class for implementing checkers game engines
	@param: board obj: board2.Board instance
	'''
	def __init__(self, board):
		self.board = board
		# if the engine returns a score, it is stored here for the most recent move returned. The score should be an integer between -100 and +100, where +100 is a win for the engine and -100 is a win for the opponent.
		self.score = None
		
	@property
	@abstractmethod
	def name(self):
		pass

	@property
	@abstractmethod
	def desc(self):
		pass

	@abstractmethod
	def selectMove( self, position, moves ):
		pass

	def __repr__(self):
		return "%s: %s" % (self.name, self.desc)
