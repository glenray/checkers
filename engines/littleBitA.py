import random
import re
import operator
import math
from engines.engine import Engine
from types import SimpleNamespace
from board2 import Board
from positions import positions
'''
littleBit: Translate board position to a bit board 
Does not select any move yet
Glen Pritchard -- 6/5/2019

A good tutorial about bitboards for checkers:
https://www.3dkingdoms.com/checkers/bitboards.htm
'''
class player(Engine):
	def __init__(self, board):
		super(player, self).__init__(board)
		self._name = "littleBitA"
		self._desc = "littleBit without using numpy.uint32 ints."
		self.bp, self.rp, self.k = 0, 0, 0
		self.emptySqs = 0
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

	def getMovers(self):
		"""
		Return a bitword of pieces that have a non-jump move.
		Square 0 is in the upper left corner.
		Empty spaces in front of the red pieces are right shifted
		to check the diagonal square for a red piece
		Kings need to check in both directions
		"""
		n = self.getSideVars()
		# Shift empty squares by 4. If that square is occupied by a 
		# man on move, then it's a move. This works for all squares. 
		movers =  n.forShift( self.emptySqs, 4 ) & n.onMove
		# Shift empty squares by 3 or 5. This works only for squares
		# specified in the respective masks
		movers |= n.forShift( self.emptySqs & n.forMsk3, 3 ) & n.onMove
		movers |= n.forShift( self.emptySqs & n.forMsk5, 5 ) & n.onMove
		if n.K:
			movers |= n.bacShift( self.emptySqs, 4 ) & n.onMove
			movers |= n.bacShift( self.emptySqs & n.kgMsk3, 3 ) & n.K
			movers |= n.bacShift( self.emptySqs & n.kgMsk5, 5 ) & n.K
		return movers

	def getJumpers(self):
		# Return a bitword of pieces that can jump.
		n = self.getSideVars()
		jumpers = 0
		Temp = n.forShift( self.emptySqs, 4 ) & n.enemy
		jumpers |= ( n.forShift( ( Temp & n.forMsk3 ), 3 ) | n.forShift( ( Temp & n.forMsk5 ), 5 ) ) & n.onMove
		Temp = (n.forShift( self.emptySqs & n.forMsk3, 3 ) | n.forShift( (self.emptySqs & n.forMsk5), 5)) & n.enemy
		jumpers |= n.forShift( Temp, 4 ) & n.onMove
		if n.K:
			Temp = n.bacShift( self.emptySqs, 4 ) & n.enemy
			jumpers |= (n.bacShift( ( Temp & n.kgMsk3 ), 3 ) | n.bacShift( ( Temp & n.kgMsk5 ), 5 )) & n.K
			Temp = ( n.bacShift( self.emptySqs & n.kgMsk3, 3 ) | n.bacShift( (self.emptySqs & n.kgMsk5), 5) ) & n.enemy
			jumpers |= n.bacShift( Temp, 4 ) & n.K
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

	def getSideVars(self, s=None):
		'''
		Return side-to-move dependent variables needed to calculate
		movers and jumpers.
		@ param int: 1 or -1 for side to move
		@ return obj: SimpleNamespace object containing the variables
		'''
		if self.sideVars == None: self.initSideVars()
		s = self.board.onMove if s == None else s
		retVal = self.sideVars[1] if s == 1 else self.sideVars[0]
		retVal.onMove = self.bp if s == 1 else self.rp
		retVal.enemy = self.rp if s == 1 else self.bp
		retVal.K = retVal.onMove & self.k
		return retVal

		# d = {
		# 	'onMove' 	: self.bp if s == 1 else self.rp,
		# 	'enemy' 	: self.rp if s == 1 else self.bp,
		# 	'forShift' 	: operator.rshift if s == 1 else operator.lshift,
		# 	'bacShift' 	: operator.lshift if s == 1 else operator.rshift,
		# 	'forMsk3' 	: self.MASK_R3 if s == 1 else self.MASK_L3,
		# 	'forMsk5' 	: self.MASK_R5 if s == 1 else self.MASK_L5,
		# 	'kgMsk3' 	: self.MASK_L3 if s == 1 else self.MASK_R3,
		# 	'kgMsk5' 	: self.MASK_L5 if s == 1 else self.MASK_R5,
		# }
		# d['K'] = d['onMove'] & self.k
		# return SimpleNamespace(**d)

	def convert2BB(self, position):
		'''
		Set bit board representation from FEN string. 
		This by setting	player.rb, player.bp, and player.k
		@param position str: FEN representation of a position
		'''
		position = re.findall(r'"([^"]*)"', position)
		sides = position[0].split(':')
		self.onMove = 1 if sides[0] == 'B' else -1
		pieces = {
			"white": (sides[1][1:] if sides[1].startswith('W') else sides[1]).split(','),
			"black": (sides[2][1:] if sides[2].startswith('B') else sides[2]).split(',')
		}
		for color in pieces:
			for sq in pieces[color]:
				pColor = 1 if color == 'black' else 3
				if sq[0] == 'K':
					# add 1 to convert piece to king no matter color, then remove K designation
					pColor = pColor+1
					sq = sq[1:]
				self.setSq(pColor, int(sq)-1)
		# Now we can extract other useful information from the bitboards
		# like the location of empty squares, ie, squares
		# containing pieces of neither color
		self.emptySqs = ~(self.rp | self.bp )

	def setSq(self, sq, i):
		'''
		Alter the bp, rp, and k bitboard words at location i
		@param sq int: piece type: 0 to 4 (Board.BP = 1, etc) 
		@param i int : the bit location within the bitboard word
		'''
		if sq == 0:
			bpBit = 0
			rpBit = 0
			kBit  = 0
		else:
			bpBit = 1 if sq < 3 else 0
			rpBit = 1 if sq > 2 else 0
			kBit  = 1 if sq % 2 == 0 else 0
		self.bp = self.modifyBit( self.bp, i, bpBit )
		self.rp = self.modifyBit( self.rp, i, rpBit )
		self.k = self.modifyBit( self.k, i, kBit )

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

	def getNormalMoves(self, movers):
		'''
		Get non-jump moves from a bit board of movers
		@ param movers: bin: bit board of non jump movers
		@ return list: list of tuples (x, y), where x is the starting
		positional bit of the piece and y is the landing square.
		'''
		n = self.getSideVars()
		moves = []
		side2move = self.board.onMove
		directions = (
			(self.emptySqs, 4),
			(self.emptySqs & n.forMsk3, 3),
			(self.emptySqs & n.forMsk5, 5)
		)
		while movers:
			x = self.getFirstSetBitPosition(movers)
			sq = self.S[x]
			for d in directions:
				if n.forShift( d[0], d[1] ) & sq:
					moves.append((x, x+(d[1]*side2move)))
			movers = self.modifyBit(movers, x, 0)
		return moves

if __name__ == '__main__':
	pos = positions['royalTour']
	b = Board()
	# b.onMove = 1
	p = player(b)
	p.convert2BB(b.pos2Fen())
	movers = p.getMovers()
	ls = b.FEN2Pos
	print(b.printBoard())
	print(p.getNormalMoves(movers))
