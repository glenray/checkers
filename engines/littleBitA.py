import math
import operator
import random
import re
from types import SimpleNamespace
from engines.engine import Engine
from board2 import Board
from positions import positions
'''
littleBitA: Modified littleBit that does not use numpy
Translate board position to a bit board 
Glen Pritchard -- 9/5/2022
'''
class player(Engine):
	def __init__(self, board):
		super(player, self).__init__(board)
		self._name = "littleBitA"
		self._desc = "littleBit without using numpy.uint32 ints."
		self.sideVars = None
		self.S = [2 ** i for i in range(32)]
		"""
		-- These left shift and right shift masks work when square 0 
		is on the top left.
		-- All squares work with shift 4. So, we don't need a mask for that.
		-- Outer edge squares (3, 4, 11, 12 ...) can only shift 4.
		-- Other squares in rows 1, 3, 5, and 7 can shift 3 
		-- Other squares in rows 0, 2, 4, and 6 can shift 5.
		   000   001   002   003
		004   005   006   007
		   008   009   010   011
		012   013   014   015
		   016   017   018   019
		020   021   022   023
		   024   025   026   027
		028   029   030   031
		"""
		self.MASK_L3 = self.S[ 5] | self.S[ 6] | self.S[ 7] | self.S[13] | self.S[14] | self.S[15] | self.S[21] | self.S[22] | self.S[23]
		self.MASK_L5 = self.S[ 0] | self.S[ 1] | self.S[ 2] | self.S[ 8] | self.S[ 9] | self.S[10] | self.S[16] | self.S[17] | self.S[18] | self.S[24]  | self.S[25]  | self.S[26]
		self.MASK_R3 = self.S[ 8] | self.S[ 9] | self.S[10] | self.S[16] | self.S[17] | self.S[18] | self.S[24] | self.S[25] | self.S[26]
		self.MASK_R5 = self.S[ 5] | self.S[ 6] | self.S[ 7] | self.S[13] | self.S[14] | self.S[15] | self.S[21] | self.S[22] | self.S[23] | self.S[29]  | self.S[30]  | self.S[31]

	# required by engine base class
	@property
	def name(self):
		return self._name
	
	@property
	def desc(self):
		return self._desc
	
	def selectMove(self, position, moves):
		if moves: self.convert2BB(position)
		# pick random move any way
		moveLen = len(moves)
		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moves[moveNo]

	def getMovers(self, position):
		"""
		Return a bitword of pieces that have a non-jump move.
		Square 0 is in the upper left corner.
		Empty spaces in front of the red pieces are right shifted
		to check the diagonal square for a red piece
		Kings need to check in both directions
		"""
		n = self.getSideVars(position)
		empty = ~(position[0] | position[1])
		# Shift empty squares by 4. If that square is occupied by a 
		# man on move, then it's a move. This works for all squares. 
		movers =  n.forShift( empty, 4 ) & n.onMove
		# Shift empty squares by 3 or 5. This works only for squares
		# specified in the respective masks
		movers |= n.forShift( empty & n.forMsk3, 3 ) & n.onMove
		movers |= n.forShift( empty & n.forMsk5, 5 ) & n.onMove
		if n.K:
			movers |= n.bacShift( empty, 4 ) & n.onMove
			movers |= n.bacShift( empty & n.kgMsk3, 3 ) & n.K
			movers |= n.bacShift( empty & n.kgMsk5, 5 ) & n.K
		return movers

	def getJumpers(self, position):
		'''
		Return a bitboard of pieces that can jump.
		@param position: list: position to look for jumpers [bp, rp, k, onMove]
		@return int: bitboard of jumpers
		'''
		n = self.getSideVars(position)
		empty = ~(position[0] | position[1])
		jumpers = 0
		# line up empty squares with the enemy
		Temp = n.forShift(empty, 4) & n.enemy
		# line up above with on move pieces
		jumpers |= (n.forShift((Temp & n.forMsk3), 3) | n.forShift((Temp & n.forMsk5), 5)) & n.onMove
		Temp = (n.forShift(empty & n.forMsk3, 3) | n.forShift((empty & n.forMsk5), 5)) & n.enemy
		jumpers |= n.forShift(Temp, 4) & n.onMove
		if n.K:
			Temp = n.bacShift(empty, 4) & n.enemy
			jumpers |= (n.bacShift((Temp & n.kgMsk3), 3) | n.bacShift(( Temp & n.kgMsk5), 5)) & n.K
			Temp = (n.bacShift(empty & n.kgMsk3, 3) | n.bacShift((empty & n.kgMsk5), 5)) & n.enemy
			jumpers |= n.bacShift(Temp, 4) & n.K
		return jumpers

	def initSideVars (self):
		black = {
			'forShift' 	: operator.rshift,
			'bacShift' 	: operator.lshift,
			'forMsk3' 	: self.MASK_R3,
			'forMsk5' 	: self.MASK_R5,
			'kgMsk3' 	: self.MASK_L3,
			'kgMsk5' 	: self.MASK_L5,
		}
		white = {
			'forShift' 	: operator.lshift,
			'bacShift' 	: operator.rshift,
			'forMsk3' 	: self.MASK_L3,
			'forMsk5' 	: self.MASK_L5,
			'kgMsk3' 	: self.MASK_R3,
			'kgMsk5' 	: self.MASK_R5,	
		}
		self.sideVars = [SimpleNamespace(**white), SimpleNamespace(**black)]

	def getSideVars(self, position):
		'''
		Return side-to-move dependent variables needed to calculate
		movers and jumpers.
		@ param int: 1 or -1 for side to move
		@ return obj: SimpleNamespace object containing the variables
		'''
		if self.sideVars == None: self.initSideVars()
		s = position[3]
		retVal = self.sideVars[1] if s == 1 else self.sideVars[0]
		retVal.onMove = position[0] if s == 1 else position[1]
		retVal.enemy = position[1] if s == 1 else position[0]
		retVal.K = retVal.onMove & position[2]
		return retVal

	def convPos2BB(self):
		'''
		Convert board2.Board FEN string to bitboards
		@return list: a list of 4 ints consisting of: 
		0: bp (bit board of black pieces), 
		1: rp (bitboard of red pieces), 
		2: kings (bitboard of kings),
		3: side on move (1 for black, -1 for white)

		'''
		position  = [0, 0, 0, 0]
		fenpos = self.board.pos2Fen()
		fenpos = re.findall(r'"([^"]*)"', fenpos)
		sides = fenpos[0].split(':')
		position[3] = 1 if sides[0] == 'B' else -1
		colors = {
			"white": (sides[1][1:] if sides[1].startswith('W') else sides[1]).split(','),
			"black": (sides[2][1:] if sides[2].startswith('B') else sides[2]).split(',')
		}
		for color in colors:
			for sq in colors[color]:
				pColor = 1 if color == 'black' else 3
				if sq[0] == 'K':
					# add 1 to convert piece to king no matter color, then remove K designation
					pColor = pColor+1
					sq = sq[1:]
				self.setSq(position, pColor, int(sq)-1)
		return position

	def setSq(self, position, man, i):
		'''
		Alter the bp, rp, and k bitboard words at location i
		@param sq int: piece type: 0 to 4 (Board.BP = 1, etc) 
		@param i int : the bit location within the bitboard word
		'''
		if man == 0:
			bpBit = 0
			rpBit = 0
			kBit  = 0
		else:
			bpBit = 1 if man < 3 else 0
			rpBit = 1 if man > 2 else 0
			kBit  = 1 if man % 2 == 0 else 0
		position[0] = self.modifyBit( position[0], i, bpBit )
		position[1] = self.modifyBit( position[1], i, rpBit )
		position[2] = self.modifyBit( position[2], i, kBit )

	def modifyBit(self, n,  p,  b):
		"""
		Return binary word with single bit changed
		@param n binary word
		@param p int position to be changed starting at 0
		@param b int new value of bit, 1 or 0
		from https://www.geeksforgeeks.org/modify-bit-given-position/
		"""
		mask = 1 << p 
		return (n & ~mask) | ((b << p) & mask)

	def countSetBits(self, n):
		'''
		Count the number of bits set in a bitboard word
		@param n bin: a 32 bit binary number (bitboard) 
		@return int: number of 1s in a bitboard word
		From https://www.geeksforgeeks.org/count-set-bits-in-an-integer/
		'''
		return (bin(n).count('1'))

	def printBB(self, bitboard):
		'''
		return human readable bitboard string
		@param bitboard: int: bitboard
		@return str: 32 character representation of bitboard
		'''
		return bin(bitboard)[2:].rjust(32, '0')

	def getFirstSetBitPosition(self, numb):
		'''
		return the position (0 based) of the right most set bit
		@ param numb: bin: a 32 bit binary number (bitboard)  
		@ return: int: 0 based position of right-most set bit. 
		Conveniently, this +1 is the FEN square number.
		From: https://btechgeeks.com/python-program-to-find-position-of-rightmost-set-bit/
		'''
		result_pos = math.log2(numb & -numb)
		return int(result_pos)

	def getNormalMoves(self, position, movers):
		'''
		Get non-jump moves from a bit board of movers
		@ param movers: bin: bit board of non jump movers
		@ return list: list of tuples (x, y), where x is the starting
		positional bit of the piece and y is the landing square.
		'''
		n = self.getSideVars(position)
		empty = ~(position[0] | position[1])
		moves = []
		side2move = position[3]
		directions = (
			(empty, 4),
			(empty & n.forMsk3, 3),
			(empty & n.forMsk5, 5)
		)
		king_directions = (
			(empty, 4),
			(empty & n.kgMsk3, 3),
			(empty & n.kgMsk5, 5)
		)
		while movers:
			x = self.getFirstSetBitPosition(movers)
			sq = self.S[x]
			for d in directions:
				if n.forShift( d[0], d[1] ) & sq:
					moves.append((x, x+(d[1]*side2move)))
			# kings look for backward moves
			if sq & position[2]:
				for kd in king_directions:
					if n.bacShift(kd[0], kd[1]) & sq:
						moves.append((x, x+(kd[1]*-side2move)))
			movers = self.modifyBit(movers, x, 0)
		return moves

	def getJumpMoves(self, position, jumpers):
		moves = []
		sideVars = self.getSideVars(position)
		while jumpers:
			x=self.getFirstSetBitPosition(jumpers)
			jumpers = self.modifyBit(jumpers, x, 0)
			moves = moves + self.jumpersRecurse(x, moves, position, sideVars)
		return moves
	
	def jumpersRecurse(self, js, moves, position, sideVars):
		empty = ~(position[0] | position[1])
		jumperSq = self.S[js]
		mip = []
		pnt = position[3]
		Temp = sideVars.forShift(empty, 4) & sideVars.enemy
		dirs = (
			(sideVars.forShift(Temp, 3) & jumperSq, 7*pnt),
			(sideVars.forShift(Temp, 5) & jumperSq, 9*pnt),
			(sideVars.forShift(Temp, 4) & jumperSq, 9*pnt)
		)
		Temp = sideVars.bacShift(empty, 4) &sideVars.enemy
		kdirs = (
			(sideVars.bacShift(Temp, 3) & jumperSq, -7*pnt),
			(sideVars.bacShift(Temp, 5) & jumperSq, -9*pnt),
			(sideVars.bacShift(Temp, 4) & jumperSq, -7*pnt),
		)
		for d in dirs:
			if d[0]:
				mip.append([js, js+d[1]])
		# for kings
		if jumperSq & position[2]:
			for d in kdirs:
				if d[0]:
					mip.append([js, js+d[1]])
		breakpoint()


	def printBoard(self, data=None):
		"""
		Display bitboard as human readable board
		@ param data: int or list: if list of 5 ints, the current position 
		is displayed as pieces (b, r, B, R). 
		Assuming list is [bp, rp, kings, emptySpaces, onmove]
		If int, the bitWord is displayed as 0s and 1s
		@ return str: a human readable checker board
		"""
		sq = 0
		spacer = "  "
		output = ""
		for row in range(8):
			s = spacer 	if row%2 == 0 else ""
			for col in range(4):
				mask = 1 << sq
				if( type(data) == list ):
					if( data[0] & mask > 0 ): s += 'b'
					elif( data[1] & mask > 0 ):	s += 'r'
					else: s += "-"
					if( data[2] & mask > 0 ): s = s.upper()
				else:
					if( data & mask>0 ): s += '1'
					else: s +='0'
				sq += 1
				output += s+spacer
				s=""
			output += "\n"
		return output

if __name__ == '__main__':
	pos = positions['multiJumpA']
	pos = positions['jump']
	pos = positions['kingJump']
	b = Board(pos)
	b.onMove *= -1
	p = player(b)
	position = p.convPos2BB()
	jumpers = p.getJumpers(position)
	p.getJumpMoves(position, jumpers)
