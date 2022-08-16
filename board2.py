import re
import copy

from positions import positions as pos

"""
Board2
Glen Pritchard 6/25/2019
- Update from board.Board.position which used an 8x8 nested list
- Maintain the state of a checkers board in a padded array of 46 elements
- Generates a list of legal moves in a given position, including multiple jumps
- Updates the board state when one of the legal moves is selected
- Ends the game when the side to move has no legal moves
Here is the layout of board2.Board.position list, where '--' are out of bounds
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
class Board:
	def __init__(self, startPos=None):
		self.OOB 	= -1  # out of bounds value
		self.EMPTY 	= 0
		self.BP 	= 1
		self.BK 	= 2
		self.WP 	= 3
		self.WK 	= 4
		# 1 = black to move; -1 white to move
		self.onMove	= None
		self.legalMoves = []
		self.isJump = False
		# list of 46 ints representing 32 board squares plus out of bounds padding
		self.position = []
		self.startFEN = '[FEN "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"]'
		self.startPos = startPos if startPos != None else self.startFEN
		# Tuple to convert FEN square no to self.position index value
		# idx+1 is FEN sq position; value is index to self.position array
		self.FEN2Pos = (37, 38, 39, 40, 32, 33, 34, 35, 28, 29, 30, 31, 23, 24, 25, 26, 19, 20, 21, 22, 14, 15, 16, 17, 10, 11, 12, 13, 5, 6, 7, 8)
		self.fen = tuple(x for x in range(1,33))
		self.pos2FEN = {v:k+1 for k,v in enumerate(self.FEN2Pos)}
		self.initEmptyBoard()
		self.parseFen()

	def getSq(self, n):
		'''
		Get a square's piece value from Board.position from FEN square number.
		n=1 will return the value of Board.position[37]
		@param n: int: a FEN square number
		@return int: the value of the square (EMPTY, BP, WP, etc) from Board.position
		'''
		return self.position[self.FEN2Pos[n-1]]

	def setSq(self, n, value):
		'''
		Set a square's piece value in Board.position given FEN square no. n
		@param n: int: a FEN Square number
		@param value: int: a piece value, EMPTY, BP, BK, WP, WK)
		'''
		self.position[self.FEN2Pos[n-1]] = value

	def reset(self):
		self.__init__()
	
	def makeMove(self, move):
		'''
		Updates Board.position to reflect the result of the selected move
		@param move list: squares involved in the move in FEN notation
		'''
		# if the move list is empty, the game is over
		# or if the user input nonsense that returns None, don't do anything
		if not move: return
		# convert FEN square numbers to self.position array indexes
		# move = [self.FEN2Pos[FENmove-1] for FENmove in move]
		# pos = self.position
		end = move[-1]
		start = move[0]
		# empty the start square and put piece on end square
		self.setSq(end, self.getSq(start))
		self.setSq(start, self.EMPTY)
		# empty jumped pieces. 
		if abs(move[0] - move[1]) > 5:
			for i, sq in enumerate(move):
				if i == 0: continue
				idx = int((move[i]+move[i-1])/2)
				self.setSq(idx, 0)
				# pos[idx] = 0
		# king piece on back row
		if end in (1,2,3,4) and self.getSq(end) == self.WP: self.setSq(end, self.WK)
		if end in (29,30,31,32) and self.getSq(end) == self.BP: self.setSq(end, self.BK)
		# toggle side to move
		self.onMove = -self.onMove

	def getLegalMoves(self):
		del self.legalMoves[:]
		self.isJump = False
		side = (self.BP,self.BK) if self.onMove == 1 else (self.WP,self.WK)
		for i, sq in enumerate(self.position):
			if sq not in (side): continue
			self.getJumpMove(i)
			if self.isJump == False:
				self.getNormalMove(i)

		# Why does this not work instead of the for loop above?? Trying to use self.FEN2Pos to interate over only valid squares, not light square or OOB. But this messes up legalMoves2FEN below. Wierd.
		# for i in self.FEN2Pos:
		# 	# breakpoint()
		# 	if self.position[i] not in (side): continue
		# 	self.getJumpMove(self.position[i])
		# 	if self.isJump == False:
		# 		self.getNormalMove(self.position[i])

	def legalMoves2FEN(self, lists = None):
		# convert every element in list from internal board array to FEN position
		# No idea why this works or what I was thinking
		if lists == None: 
			self.getLegalMoves()
			lists = self.legalMoves
		return [self.pos2FEN[el] if isinstance(el, int) else self.legalMoves2FEN(el) for el in lists]

	def getNormalMove(self, sq):
		# kings look forward and backward for a move
		isKing = self.position[sq] in (self.WK, self.BK)
		directions = [-self.onMove, self.onMove] if isKing else [-self.onMove]
		for target in (4,5):
			for direction in directions:
				if self.position[sq+(direction*target)] == self.EMPTY:
					self.legalMoves.append([sq, sq+(direction*target)])
	
	def getJumpMove(self, sq, position=None, moves=[]):
		if position == None: 
			position = self.position
		# kings look forward and backward for a move
		isKing = position[sq] in (self.WK, self.BK)
		directions = [-self.onMove, self.onMove] if isKing else [-self.onMove]
		enemy = (self.BP, self.BK) if self.onMove == -1 else (self.WP, self.WK)
		newMoves = None
		# all pieces look left and right
		for target in (4,5):
			for direction in directions:
				enemySq = sq+(direction*target)
				landingSq = sq+(direction*target*2)
				if position[enemySq] in (enemy) and position[landingSq] == self.EMPTY:
					# if this is the first jump detected, clear the move list
					if self.isJump == False:
						self.isJump = True
						del self.legalMoves[:]
					newPosition = copy.copy(position)
					# move piece to landing square; clear origin and enemy squares
					newPosition[landingSq] = newPosition[sq]
					newPosition[sq] = 0
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
		self.position = [self.EMPTY]*46
		# set out of bounds squares
		for i in [0,1,2,3,4,9,18,27,36,41,42,43,44,45]:
			self.position[i] = self.OOB

	def printBoard(self, position=None):
		'''
		Returns a string of the position in human readable form

		param: list: The Board.position, the internal representation of a board position
		return: str: Human readable representation of the board position.
		'''
		position = self.position if position==None else position
		border = "    -----------------"
		offset, output, sqNum = "  ", f'\n{self.pos2Fen()}\n{border}\n', 1
		for start in [37, 32, 28, 23, 19, 14, 10, 5]:
			output+= "{:>2} | ".format(sqNum)
			sqNum +=3
			rowtxt = offset
			for row in range(0,4):
				sq = position[start+row]
				char = 'b' if sq in (1,2) else 'w'
				char = char.upper() if sq %2 == 0 else char
				if sq == 0: char='-'
				rowtxt += char+"   "
			rowtxt = rowtxt.rstrip().ljust(16)
			output += rowtxt+"| {0}\n".format(sqNum)
			sqNum += 1
			offset = '' if offset == "  " else "  "
		return output+border

	def parseFen(self, FEN=None):
		# import position from FEN string
		if FEN == None:
			FEN = self.startPos
		# FEN[0] will be a string of what is inside double quotes of the 
		# original FEN string passed to the function
		FEN = re.findall(r'"([^"]*)"', FEN)
		sides = FEN[0].split(':')
		self.onMove = 1 if sides[0] == 'B' else -1
		pieces = {
			"white": (sides[1][1:] if sides[1].startswith('W') else sides[1]).split(','),
			"black": (sides[2][1:] if sides[2].startswith('B') else sides[2]).split(',')
		}
		
		for color in pieces:
			for sq in pieces[color]:
				pColor = self.BP if color == 'black' else self.WP
				if sq[0] == 'K':
					# add 1 to convert piece to king no matter color, then remove K designation
					pColor = pColor+1
					sq = sq[1:]
				self.position[self.FEN2Pos[int(sq)-1]] = pColor

	def pos2Fen(self):
		# create FEN string from current position
		black, white = [], []
		onMove = "B" if self.onMove == 1 else "W"
		for i, sq in enumerate(self.position):
			if self.position[i] > 0:
				sqNo = str(self.pos2FEN[i])
				king = "K" if self.position[i] in (self.BK, self.WK) else ""
				if self.position[i] > 2:
					white.append(f"{king}{sqNo}")
				else:
					black.append(f"{king}{sqNo}")
		black = ','.join(black)
		white = ','.join(white)
		return f'[FEN "{onMove}:W{white}:B{black}"]'

if __name__ == "__main__" :
	a = Board('[FEN "B:W18,26,27,25,11,19:B15K"]')
	a.getLegalMoves()
	print(legalMoves2FEN())
	quit()
	move = [9, 13]
	a.makeMove(move)
	print(a.printBoard())