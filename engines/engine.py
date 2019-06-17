from abc import ABC, abstractmethod, abstractproperty

class Engine(ABC):
	def __init__(self, board):
		self.board = board
		
	@property
	@abstractmethod
	def name(self):
		pass

	@property
	@abstractmethod
	def desc(self):
		pass

	@abstractmethod
	def selectMove( self ):
		pass

	def __repr__(self):
		return "%s: %s" % (self.name, self.desc)
