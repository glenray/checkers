from board2 import Board
import engines
from positions import positions as pos

class Play:
	'''
	Play checkers where either player can be an engine or a human
	Glen Pritchard -- 8/13/2022
	@param board: obj: instance of board2.Board class
	@param bp: obj or str: an engine object or "human" to play black
	@param rp: obj or str: an engine object or "human" to play white (red)
	'''
	helpScreen = '''Available commands:
	q \tQuit
	(f)en \tShow FEN notation of current position
	(b)oard \tShow the current board and legal moves
'''
	def __init__(self, board, bp, rp):
		self.board = board
		self.bp = bp
		self.rp = rp
		self.run()

	def run(self):
		self.displayGameIntro()
		print(self.board.printBoard())
		while True:
			sidetomove = "Black" if self.board.onMove == 1 else "White"
			player = self.bp if sidetomove == "Black" else self.rp
			print(f"{sidetomove} ({player.name}) to move:")
			self.board.getLegalMoves()
			legalMoves = self.board.legalMoves2FEN()
			if len(legalMoves) == 0:
				self.declareWinner(sidetomove)
				break
			if player == 'human':
				move = self.getHumanMove(legalMoves)
			else:
				n = len(legalMoves)
				twoB = 'are' if n > 1 else 'is'
				print(f"{n} moves {twoB} possible: {self.board.legalMoves2FEN()}")
				print(f"{player.name} is thinking...", end='\r')
				move = player.selectMove(legalMoves)
				print(f"{player.name} plays {move}\n(Score: {player.score}; Nodes: {player.totalNodes}; Time: {player.elapsedTime}; NPS: {player.nps})")
			self.board.makeMove(move)
			print(self.board.printBoard())

	def declareWinner(self, sidetomove):
		winner = "White" if sidetomove == "Black" else "Black"
		print(f"{sidetomove} has no moves left. {winner} wins!")

	def getHumanMove(self, legalMoves):
		'''
		Return a move from the human user.
		@param legalMoves: list a list of legal moves in FEN notation
		@return list: one element from legalMoves
		'''
		def askHuman4Move():
			print("Here are the legal moves:")
			for i, move in enumerate(legalMoves):
				print(f"{i}. {move}")

		askHuman4Move()
		while True:
			inp_range = f"0-{len(legalMoves)-1}" if len(legalMoves) > 1 else '0' 
			hMove = input(f"What is your move, Human? \n({inp_range} to move or 'h' for other commands): ")
			if hMove == 'q'.lower():
				print("Quitting")
				quit()
			if hMove.lower() == 'fen' or hMove.lower() == 'f':
				print(f"The current board position is: \n{self.board.pos2Fen()}")
				continue
			if hMove.lower() == 'help' or hMove.lower() == 'h':
				print(Play.helpScreen)
				continue
			if hMove.lower() == 'b' or hMove.lower == 'board':
				print(self.board.printBoard())
				askHuman4Move()
				continue
			try:
				x = int(hMove)
			except:
				print("Your input is not an integer. Try again.")
				continue
			if x >= 0 and x<len(legalMoves):
				return legalMoves[x]
			else:
				print(f"Your input must be {inp_range}. Try again.")
				continue

	def displayGameIntro(self):
		print(f"Black: {self.bp} vs. White: {self.rp}")


def main():
	pos = '[FEN "W:W27,18,11,6,K1:B25,26,28,17,19,20,9,10,2,4"]'
	b = Board()
	rp = engines.minmaxB(b, maxdepth=10, ab=True)
	bp = engines.minmaxB(b, maxdepth=5, ab=True)
	Play(b, bp, rp)

if __name__ == '__main__':
	main()