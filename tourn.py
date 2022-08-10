'''
Run tournament between 2 engines
'''
import importlib
import pkgutil
import sys

from board2 import Board as board
from debug import debug

class Tourn():
	def __init__(self, bp=None, rp=None, n=10):
		'''
		param bp: str: Name of an engine to play black
		param wp: str: Name of an engine to play white
		param n:  int: Number of games to play in tournament
		'''
		self.b = board()
		self.db = debug()
		self.red = 0		# red win count
		self.black = 0		# black win count
		self.draw = 0		# draw count
		self.mostMoves = 0
		self.moveNo = 1
		self.engineNames = self.getEngineNames()
		self.setTournParams(bp, rp, n)
		self.runTournament()
		self.printResult()

	def setTournParams(self, bp, rp, n):
		'''
		Sets the engine for each player and the number of games to play
		'''
		if bp in self.engineNames and rp in self.engineNames:
			self.bp = self.getEngine(bp)
			self.rp = self.getEngine(rp)
			self.n = n
		else:
			self.getUserInput()

	def getEngine(self, eng_name):
		im = importlib.import_module
		return getattr(im(f"engines.{eng_name}"), 'player')(self.b)

	def getUserInput( self ):
		engines = []
		print("Engine Choices")
		for i, engineName in enumerate(self.engineNames):
			engines.append(self.getEngine(engineName))
			print( i, engines[i] )

		self.bp = engines[int(input("Engine No for Black: "))]
		self.rp = engines[int(input("Engine No for Red: "))]
		self.n = int(input("How many games: "))

	def getEngineNames(self):
		'''
		return: list: names of the engines found in the engines folder
		'''
		r = [name for _, name, _ in pkgutil.iter_modules(['engines'])]
		r.remove('engine')
		return r

	def runTournament( self ):
		for a in range(1, self.n+1): 
			# Play the game until no legal moves left
			isdraw = False
			self.moveNo = 1
			self.b.getLegalMoves()
			while self.b.legalMoves and isdraw == False:
				# print(self.b.printBoard())
				# select player on move
				player = self.bp if self.b.onMove == 1 else self.rp
				# ask engine to select move
				move = player.selectMove(self.b.pos2Fen(), self.b.legalMoves2FEN())
				self.moveNo +=1
				# declare draw if 1000 moves without victory
				if self.moveNo == 1000:
					isdraw = True
				# make move selected by engine
				self.b.makeMove(move)

			# update counters; print game message
			if isdraw == True:
				self.draw += 1
				message = f"Game {a}: Draw"
			elif (self.b.onMove==1):
				self.red +=1
				message = f'Game {a} won by {self.rp.name} in {self.moveNo} moves.'
			else:
				self.black += 1
				message = f'Game {a} won by {self.bp.name} in {self.moveNo} moves.'
			print(message)
			
			if self.moveNo > self.mostMoves and isdraw == False:
				self.mostMoves = self.moveNo
			
			# start the next game
			self.b.reset()

	def printResult( self ):
		# print final tournament results
		print("\nTournament Results")
		print(f"{self.bp.name} as Black: {self.black}")
		print(f"{self.rp.name} as Red: {self.red}")
		print(f"Draws: {self.draw}")
		print(f"Most Moves (when game not a draw): {self.mostMoves}")

if __name__ == "__main__" :
	Tourn("minmaxA", "moron", 5)