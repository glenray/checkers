import os
import re
import string
import copy

'''
Checkers
Glen Pritchard 6/17/2018
- Maintain the state of a checkers board on an 8x8 array
- Generates a list of legal moves in a given position, including multiple jumps
- Updates the board state when one of the legal moves is selected
- Ends the game when the side to move has no legal moves
''' 
class Board:
	def __init__(self, startPos=None):
		'''
		Initialize empty 8x8 board array. Each element of the array can have the following values
			0: empty
			1: black piece
			2: black king
			3: white piece
			4: white king
		The upper left corner of the board is coordinate [0][0]. It is a light square, so always empty.
		
		Here is the initial board position:
		============================
		row  Squares in row
		============================
		0   [0, 1, 0, 1, 0, 1, 0, 1]
		1   [1, 0, 1, 0, 1, 0, 1, 0]
		2   [0, 1, 0, 1, 0, 1, 0, 1]
		3   [0, 0, 0, 0, 0, 0, 0, 0]
		4   [0, 0, 0, 0, 0, 0, 0, 0]
		5   [3, 0, 3, 0, 3, 0, 3, 0]
		6   [0, 3, 0, 3, 0, 3, 0, 3]
		7   [3, 0, 3, 0, 3, 0, 3, 0]
		'''
		self.position = self.clearBoard()
		self.startPos = startPos if startPos != None else '[FEN "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"]'
		# side to move, 1 for Black or -1 for Red
		self.onMove = None
		# If true, a jump for the side on move has been detected and normal moves are illegal and need not be considered
		self.isJump = False
		self.legalMoves = []
		self.FENparse(self.startPos)

	def reset(self):
		self.__init__()

	def makeMove(self, move):
		if not move: return
		position = self.position
		end = move[-1]
		start = move[0]

		# update start and end squares
		position[end[0]][end[1]] = position[start[0]][start[1]]
		position[start[0]][start[1]] = 0

		# is this a jump move
		if abs(move[0][0] - move[1][0]) == 2:
			# remove jumped pieces
			for i, sq in enumerate(move):
				if i == 0:
					continue
				jY = int((sq[0]+move[i-1][0])/2)
				jX = int((sq[1]+move[i-1][1])/2)
				position[jY][jX] = 0

		# king promotion
		if end[0] == 0 and position[end[0]][end[1]] == 3:
			position[end[0]][end[1]] = 4
		if end[0] == 7 and position[end[0]][end[1]] == 1:
			position[end[0]][end[1]] = 2
		
		# self.position = position

		# toggle side to move
		self.onMove = -self.onMove

	'''
	Search self.position for pieces having color on move
	When a piece is found, see if it has any jump moves
	If no jump moves have been found, see if there are any normal moves
	'''
	def getLegalMoves(self):
		# make sure the list is empty
		del self.legalMoves[:]
		self.isJump = False
		color = (1,2) if self.onMove == 1 else (3,4)
		# interate each row
		for Yidx, y in enumerate(self.position):
			# iterate each square in row
			for Xidx, squareValue in enumerate(y):
				# find squares containing pieces whose color is on move 
				if squareValue in color:
					# if piece, look only forward; if a king, look forward and backward
					rowDirection = (-self.onMove, self.onMove) if squareValue in (2,4) else (self.onMove,)
					# Look for jump moves
					self.jumpMove( Yidx, Xidx, rowDirection )
					# don't bother looking for normal moves if a jump has already been detected
					if self.isJump == False:
						# Look for normal moves
						self.normalMove( Yidx, Xidx, rowDirection )

	'''
	At this point, we have determined that the square at 
	self.position[Yidx][Xidx] contains a piece with the color on move
	Now we determine if that piece has a valid jump move
	When the first jump is found, self.isJump is set to true to prevent consideration of further normal moves,
	and self.legalMoves is emptied of any normal moves
	'''
	def jumpMove(self, Yidx, Xidx, rowDirection, position = None, moves=[]):
		position = self.position if position == None else position
		pieces2Attack = (3,4) if self.onMove == 1 else (1,2)
		newMoves = None
		# look at rows forward (and backward if king)
		for RDir in rowDirection:
			# look at columns to left and right
			for CDir in (1, -1):
				attackRow = Yidx+RDir
				attackCol = Xidx+CDir
				landingRow = Yidx+RDir*2
				landingCol = Xidx+CDir*2

				# consider this move only if attacked square and landing square are legal
				if(	0 <= attackRow <= 7 and 0 <= attackCol <= 7 and
					0 <= landingRow <= 7 and 0 <= landingCol <= 7):

					isEnemy = position[attackRow][attackCol] in pieces2Attack
					isPlace2Land = position[landingRow][landingCol] == 0
					# is jump possible?
					if isEnemy and isPlace2Land:
						# if this is the first jump move detected, empty the move list 
						if self.isJump == False:
							self.isJump = True
							del self.legalMoves[:]

						# create a new position after the jump
						newPosition = copy.deepcopy(position)
						# put current piece to landing square
						newPosition[landingRow][landingCol] = newPosition[Yidx][Xidx]
						# clear current square
						newPosition[Yidx][Xidx] = 0
						# clear attacked piece
						newPosition[attackRow][attackCol] = 0
						
						# add current square at beginning if this is a new series of jumps; otherwide, add the landing square only
						newMoves = moves+[(Yidx, Xidx),(landingRow, landingCol)] if moves == [] else moves+[(landingRow, landingCol)]
						# recurse with the new position; are there more jumps?
						self.jumpMove(landingRow, landingCol, rowDirection, newPosition, newMoves )
				

		# if you get to this point, the piece on move has looked in all directions and there are no further jumps; otherwise, the code would have recursed above.
		# if newMoves is still None, then the piece has looked in all legal directions without finding a jump
		# if moves is not empty, then jumps were found on previous iterations
		# if both are true, then this line of moves is the end of the line of jumps and should be added to the legal move list
		# if both conditions are not true, then there are no jump moves to add for this piece. The method will not return anything, and getLegalMoves() will continue processing the pieces.
		if newMoves == None and moves:
			self.legalMoves.append(moves)

	'''
	At this point, we have determined that the square at 
	self.position[Yidx][Xidx] contains a piece with the color on move
	Now we determine if adjacent squares are available for a legal move.
	If so, the move is added to the move list
	'''
	def normalMove(self, Yidx, Xidx, rowDirection):
		# look at rows forward (and backward if king)
		for RDir in rowDirection:
			# look at columns to left and right
			for CDir in (1, -1):
				moveRow = Yidx+RDir
				moveCol = Xidx+CDir
				# skip this move if destination square is out of bounds
				if 0 <= moveRow <= 7 and 0 <= moveCol <= 7:
					# is the destination square empty
					if self.position[moveRow][moveCol] == 0:
						# It's a valid move! Add it to the legal move list.
						self.legalMoves.append([(Yidx, Xidx),(moveRow, moveCol)])

	def clearBoard(self):
		self.onMove = None
		return [[0 for x in range(8)] for y in range(8)]

	def FENparse(self, position=None):
		if position==None:
			position = self.startPos

		position = re.findall(r'"([^"]*)"', position)
		sides = position[0].split(':')
		onMove = 1 if sides[0] == 'B' else -1
		pieces = {
			"white": sides[1].split(','),
			"black": sides[2].split(',') 
		}

		self.onMove = onMove

		for side in ('white', 'black'):
			for x in pieces[side]:
				squareNo = x[1:]  if x.startswith('W') or x.startswith('B') else x 
				if x.endswith('K'):
					isKing = True
					squareNo = squareNo[:-1]
				else:
					isKing = False
				self.setSquare((isKing, int(squareNo), side))

	def setSquare(self, args):
		coord = self.getBoardCoord(args[1])
		if args[2] == 'white':
			value = 3 if args[0] == False else 4
		else:
			value = 1 if args[0] == False else 2
		self.position[coord[1]][coord[0]] = value

	# FEN square number goes in; board row,column coordinate comes out
	def getBoardCoord(self, squareNum):	
		y = int(squareNum/4)
		x = squareNum%4
		if x==0:
			y=y-1
			x=4
		x=x*2-1
		# pad one if its an odd row
		if y%2 != 0:
			x=x-1
		return (x,y)