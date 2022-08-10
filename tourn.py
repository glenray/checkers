'''
Run tournament between 2 engines
'''
import importlib
import pkgutil
import sys

from board2 import Board
import engines

class Tourn():
	def __init__(self, board, bp, rp, n=10):
		'''
		param bp: obj: An engine instance to play black
		param wp: obj: An engine instance to play white
		param n:  int: Number of games to play in tournament
		'''
		self.b = board
		self.redWins = 0		# red win count
		self.blackWins = 0		# black win count
		self.draws = 0		# draw count
		self.mostMoves = 0
		self.moveNo = 1
		self.bp = bp
		self.rp = rp
		self.n = n
		self.runTournament()
		self.printResult()

	def runTournament(self):
		'''
		Play n number of games
		'''
		for a in range(self.n): 
			isdraw = False
			self.moveNo = 1
			self.b.getLegalMoves()
			# Play the game until no legal moves left
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

			self.printGameResult(a+1, isdraw)	
			# reset the board for the next game
			self.b.reset()

	def printGameResult(self, gameNo, isdraw):
		# update counters; print game message
		winMessage = 'Game {0} won by {1} in {2} moves.'
		drawMessage = f"Game {gameNo}: Draw"
		if isdraw == True:
			self.draws += 1
			message = drawMessage
		elif (self.b.onMove==1):
			self.redWins +=1
			message = winMessage.format(gameNo, self.rp.name, self.moveNo)
		else:
			self.blackWins += 1
			message = winMessage.format(gameNo, self.bp.name, self.moveNo)
		print(message)
		
		if self.moveNo > self.mostMoves and isdraw == False:
			self.mostMoves = self.moveNo


	def printResult( self ):
		# print final tournament results
		print("\nTournament Results")
		print(f"{self.bp.name} as Black: {self.blackWins}")
		print(f"{self.rp.name} as Red: {self.redWins}")
		print(f"Draws: {self.draws}")
		print(f"Most Moves (when game not a draw): {self.mostMoves}")

if __name__ == "__main__" :
	b = Board()
	moron = engines.moron(b)
	minmax = engines.minmaxA(b, depth=3)
	snap = engines.snap(b)
	Tourn(board=b, bp=minmax, rp=moron, n=3)