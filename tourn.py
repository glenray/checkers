'''
Run tournament between 2 engines
'''
import sys
import importlib
from board2 import Board as board
from debug import debug
import pkgutil

class Tourn():

	def __init__(self):
		self.b = board()
		self.db = debug()
		self.red = 0		# red win count
		self.black = 0		# black win count
		self.draw = 0		# draw count
		self.mostMoves = 0

		self.getUserInput()
		self.runTournament()
		self.printResult()

	def getUserInput( self ):
		engines = []
		engineNames = [name for _, name, _ in pkgutil.iter_modules(['engines'])]
		engineNames.remove('engine')

		print("Engine Choices")
		for i, engineName in enumerate( engineNames ):
			engines.insert(i, getattr(importlib.import_module("engines." + engineName), 'player')(self.b))
			print( i, engines[i] )

		self.bp = engines[int(input("Engine No for Black: "))]
		self.rp = engines[int(input("Engine No for Red: "))]
		self.n = int(input("How many games: "))

	def runTournament( self ):
		for a in range(1, self.n+1): 
			# Play the game until no legal moves left
			isdraw = False
			moveNo = 1
			self.b.getLegalMoves()
			while self.b.legalMoves and isdraw == False:
				# select player on move
				player = self.bp if self.b.onMove == 1 else self.rp
				# ask engine to select move
				move = player.selectMove(self.b.pos2Fen(), self.b.legalMoves2FEN())
				moveNo +=1
				# declare draw if 1000 moves without victory
				if moveNo == 1000:
					isdraw = True
				# make move selected by engine
				self.b.makeMove(move)

			# update counters; print game message
			if isdraw == True:
				self.draw += 1
				message = f"Game {a}: Draw"
			elif (self.b.onMove==1):
				self.red +=1
				message = f'Game {a} won by {self.rp.name} in {moveNo} moves.'
			else:
				self.black += 1
				message = f'Game {a} won by {self.bp.name} in {moveNo} moves.'
			print(message)
			
			if moveNo > self.mostMoves and isdraw == False:
				self.mostMoves = moveNo
			
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
	Tourn()