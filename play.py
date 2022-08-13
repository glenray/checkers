from board2 import Board
import engines

class Play:
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
			print(f"{sidetomove} to move:")
			self.board.getLegalMoves()
			legalMoves = self.board.legalMoves2FEN()
			if len(legalMoves) == 0:
				self.declareWinner(sidetomove)
				break
			if player == 'human':
				move = self.getHumanMove(legalMoves)
			else:
				move, value = player.selectMove(legalMoves)
			self.board.makeMove(move)
			print(self.board.printBoard())

	def declareWinner(self, sidetomove):
		winner = "White" if sidetomove == "Black" else "Black"
		print(f"{sidetomove} has no moves left. {winner} wins!")

	def getHumanMove(self, legalMoves):
		print("Here are the legal moves:")
		for i, move in enumerate(legalMoves):
			print(f"{i}. {move}")
		hMove = int(input("What is your move, Human? "))
		return legalMoves[hMove]

	def displayGameIntro(self):
		print(f"Black: {self.bp} vs. White: {self.rp}")


def main():
	pos = '[FEN "B:W18,26,27,25,11,19:BK15"]'
	b = Board(pos)
	bp = "human"
	rp = engines.minmaxA(b)
	Play(b, bp, rp)

if __name__ == '__main__':
	main()