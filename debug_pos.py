class Debug_pos:
	'''
	Get an engines evaluation of a position
	@param board: obj board2.Board instance
	@param engine: obj search engine instance
	@return tuple: the engines move in FEN square notation, the engine instance
	'''
	def __init__(self, board, engine):
		self.board = board
		self.engine = engine
		self.sides = {1 : "Black", -1 : "White"}

	def debug(self):
		print(f"{self.engine.name} to move as {self.sides[self.board.onMove]}.")
		print("Thinking...", end='\r')
		move = self.engine.selectMove()
		return move, self.engine

	def getEngineInfo(self, move):
		return f"{self.engine.name} - {self.sides[self.engine.board.onMove]}'s Move: {move}\nScore: {self.engine.score}; Time: {self.engine.elapsedTime}; Nodes: {self.engine.totalNodes}; nps: {self.engine.nps})"
