'''
Run tournament between 2 engines
'''
import os
import sys

from board2 import Board
import engines

class Tourn():
	def __init__(self, board, bp, rp, n=10, logFile=None):
		'''
		param board: obj: A Board instance to keep track of the game
		param bp: obj: An engine instance to play black
		param wp: obj: An engine instance to play white
		param n:  int: Number of games to play in tournament
		param logFile: str: Name of log file
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
		self.logFile = logFile
		self.runTournament()
		self.printTournamentResult()

	def runTournament(self):
		'''
		Play n number of games
		'''
		if self.logFile and os.path.exists(self.logFile):
			os.remove(self.logFile)
		for a in range(self.n): 
			isdraw = False
			self.moveNo = 1
			self.b.getLegalMoves()
			# Play the game until no legal moves left
			while len(self.b.legalMoves) and isdraw == False:
				# select player on move
				player = self.bp if self.b.onMove == 1 else self.rp
				# ask engine to select move
				move = player.selectMove(self.b.pos2Fen(), self.b.legalMoves2FEN())
				if self.logFile:
					self.logger(player, ev, move)
				self.moveNo +=1
				# declare draw if 1000 moves without victory
				if self.moveNo == 1000:
					isdraw = True
				# make move selected by engine
				self.b.makeMove(move)
				self.b.getLegalMoves()

			self.printGameResult(a+1, isdraw)	
			# reset the board for the next game
			self.b.reset()

	def logger(self, player, ev, move):
		'''
		Print each move and score to a log file
		'''
		with open(self.logFile, 'a') as f:
			f.write(f"{player.name}, {move}, {ev}, {self.b.pos2Fen()}\n")
			f.write(self.b.printBoard()+"\n")

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
		# track the game with the most moves
		if self.moveNo > self.mostMoves and isdraw == False:
			self.mostMoves = self.moveNo
		print(message)

	def printTournamentResult(self):
		# print final tournament results
		print("\nTournament Results")
		print(f"{self.bp.name} as Black: {self.blackWins}")
		print(f"{self.rp.name} as Red: {self.redWins}")
		print(f"Draws: {self.draws}")
		print(f"Most Moves (when game not a draw): {self.mostMoves}")

if __name__ == "__main__" :
	b = Board()
	moron = engines.moron(b)
	minmax3 = engines.minmaxA(b, maxdepth=3)
	minmax5 = engines.minmaxB(b, maxdepth=5)
	snap = engines.snap(b)
	Tourn(board=b, bp=minmax3, rp=minmax5, n=5)