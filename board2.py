import re
import copy

"""
Board2
Glen Pritchard 6/25/2019
- Update from board.py which used an 8x8 nested array
- Maintain the state of a checkers board in a padded array of 46 elements
- Generates a list of legal moves in a given position, including multiple jumps
- Updates the board state when one of the legal moves is selected
- Ends the game when the side to move has no legal moves
"""
class Board:
	
	def __init__(self, startPos=None):
		self.templ = """
  --  --  --  --  --
    37  38  39  40
  32  33  34  35  --
    28  29  30  31
  23  24  25  26  --
    19  20  21  22
  14  15  16  17  --
    10  11  12  13
  05  06  07  08  --
--  --  --  --  --
"""
		self.OOB 	= -1  # out of bounds value
		self.EMPTY 	= 0
		self.BP 	= 1
		self.BK 	= 2
		self.WP 	= 3
		self.WK 	= 4
		self.onMove	= None
		self.legalMoves = []
		self.isJump = False
		self.position= {}
		self.startFEN= '[FEN "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"]'
		self.startPos= startPos if startPos != None else self.startFEN
		# Array to convert FEN square no to self.position index value
		# idx+1 is FEN sq position; value is index to self.position array
		self.FEN2Pos = [37, 38, 39, 40, 32, 33, 34, 35, 28, 29, 30, 31, 23, 24, 25, 26, 19, 20, 21, 22,14, 15, 16, 17, 10, 11, 12, 13, 5, 6, 7, 8]

		self.initEmptyBoard()
		self.parseFen()
		

	def reset(self):
		self.__init__()
	
	def makeMove(self, move):
		print(self.legalMoves)
		# if not move: return
		pos = self.position
		end = move[-1]
		start = move[0]

		pos[end] = pos[start]
		pos[start] = 0

		# jump moves, i.e. any move more than 5
		if abs(move[0] - move[1]) > 5:
			for i, sq in enumerate(move):
				if i == 0: continue
				pos[(move[i]+move[i-1])/2] = 0

		# king piece on back row
		if end in (37, 38, 29, 40) and pos[end] == self.WP: pos[end] = self.WK
		if end in (5, 6, 7, 8) and pos[end] == self.BP: pos[end] = self.BK


		print(self.onMove)
		print(move)
		self.printBoard()
		print(self.pos2Fen())
		ans = input("Continue? ")
		if ans == 'stop': exit()

		# toggle side to move
		self.onMove = -self.onMove


	def getLegalMoves(self):
		del self.legalMoves[:]
		self.isJump = False
		side = (self.BP,self.BK) if self.onMove == 1 else (self.WP,self.BP)
		for sq in self.position:
			if self.position[sq] not in (side): continue
			self.getJumpMove(sq)
			if self.isJump == False:
				self.getNormalMove(sq)

	
	def getNormalMove(self, sq):
		# kings look forward and backward for a move
		isKing = self.position[sq] % 2 == 0
		OM = self.onMove
		directions = [-OM, OM] if isKing else [-OM]
		for target in (4,5):
			for direction in directions:
				if self.position[sq+(direction*target)] == self.EMPTY:
					self.legalMoves.append([sq, sq+(direction*target)])
	
	
	def getJumpMove(self, sq, position=None, moves=[]):
		if position == None: 
			position = self.position
		# kings look forward and backward for a move
		isKing = self.position[sq] % 2 == 0
		OM = self.onMove
		directions = [-OM, OM] if isKing else [-OM]
		enemy = (1,2) if OM == -1 else (3,4)
		newMoves = None
		# all pieces look left and right
		for target in (4,5):
			for direction in directions:
				enemySq = sq+(direction*target)
				landingSq = sq+(direction*target*2)
				if position[enemySq] in (enemy):
					if position[landingSq] == self.EMPTY:
						if self.isJump == False:
							self.isJump = True
							del self.legalMoves[:]
						
						newPosition = copy.deepcopy(position)
						# copy current piece to new position
						newPosition[landingSq] = newPosition[sq]
						# clear current piece square
						newPosition[sq] = 0
						# remove jumped piece
						newPosition[enemySq] = 0
						newMoves = [sq, landingSq] if moves == [] else moves+[landingSq]
						self.getJumpMove(landingSq, newPosition, newMoves)
		# at this point, the piece on move has looked in all directions and there are no further jumps; otherwise, the code would have recursed above.
		# if newMoves is still None, then the piece has looked in all legal directions without finding a jump
		# if moves is not empty, then jumps were found on previous iterations
		# if both are true, then this line of moves is the end of the line of jumps and should be added to the legal move list
		# if both conditions are not true, then there are no jump moves to add for this piece. The method will not return anything, and getLegalMoves() will continue processing the pieces.
		if newMoves == None and moves:
			self.legalMoves.append(moves)

	
	def initEmptyBoard(self):
		# init empty position
		offLimits = [0,1,2,3,4,9,18,27,36,41,42,43,44,45]
		for sq in range(0, 46):
			self.position[sq] = self.OOB if sq in offLimits else self.EMPTY


	def printBoard(self, position=None):
		position = self.position if position==None else position
		offset = "  "
		for start in [37, 32, 28, 23, 19, 14, 10, 5]:
			output = ''
			for row in range(0,4):
				sq = position[start+row]
				char = 'b' if sq in (1,2) else 'w'
				char = char.upper() if sq %2 == 0 else char
				if sq == 0: char='-'
				output += char+"   "
			print(offset, output)
			offset = '' if offset == "  " else "  "

	# import position from FEN string
	def parseFen(self, position=None):
		if position==None:
			position = self.startPos

		position = re.findall(r'"([^"]*)"', position)
		sides = position[0].split(':')
		self.onMove = 1 if sides[0] == 'B' else -1
		pieces = {
			"white": (sides[1][1:] if sides[1].startswith('W') else sides[1]).split(','),
			"black": (sides[2][1:] if sides[2].startswith('B') else sides[2]).split(',')
		}
		
		for color in pieces:
			for sq in pieces[color]:
				pColor = self.BP if color == 'black' else self.WP
				if sq[-1:] == 'K':
					# add 1 to convert piece to king not matter color, then remove K designation
					pColor = pColor+1
					sq = sq[:-1]
				
				self.position[self.FEN2Pos[int(sq)-1]] = pColor

	# create FEN string from current position
	def pos2Fen(self):
		black = blacksep = white = whitesep = ""
		onMove = "B" if self.onMove == 1 else "W"
		for sq in self.position:
			if self.position[sq] > 0:
				sqNo = str(self.FEN2Pos.index(sq)+1)
				king = "K" if self.position[sq]%2 == 0 else ""
				if self.position[sq] > 2:
					white += f"{whitesep}{sqNo}{king}"
					whitesep = ","
				else:
					black += f"{blacksep}{sqNo}{king}"
					blacksep = ","
		return f'[FEN "{onMove}:W{white}:B{black}"]'


if __name__ == "__main__" :
	pos = '[FEN "B:W18,26,27,25,11,19:B15K"]'
	a = Board()
	print(a.templ)
	a.printBoard()
	a.getLegalMoves()
	color = 'Black' if a.onMove == 1 else "White"
	print(f"{color} on Move")
	for move in a.legalMoves:
		print(move)
	a.makeMove(a.legalMoves[0])
	a.printBoard()
	a.getLegalMoves()
	color = 'Black' if a.onMove == 1 else "White"
	print(f"{color} on Move")
	for move in a.legalMoves:
		print(move)