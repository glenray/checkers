import random
import operator
import numpy as np
from engines.engine import Engine
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
		self._name = "littleBit"
		self._desc = "I translate the position into a bit board. No move selection yet."
		self.bp = np.uint32(0)
		self.rp = np.uint32(0)
		self.k =  np.uint32(0)
		self.emptySqs = np.uint32(0)
		self.S = []
		self.S.append(1)
		for  i in range(1, 32):
			self.S.append( np.uint32(self.S[i-1] * 2) )
		# This mask work when square 0 is on the top left
		"""
		  00  01  02  03
		04  05  06  07
		  08  09  10  11
		12  13  14  15
		  16  17  18  19
		20  21  22  23
		  24  25  26  27
		28  29  30  31
		"""
		self.MASK_L3 = self.S[5] | self.S[6] | self.S[7] | self.S[13] | self.S[14] | self.S[15] | self.S[21] | self.S[22] | self.S[23]
		self.MASK_L5 = self.S[0] | self.S[1] | self.S[2] | self.S[8] | self.S[9] | self.S[10] | self.S[16] | self.S[17] | self.S[18] | self.S[24]  | self.S[25]  | self.S[26]
		self.MASK_R3 = self.S[8] | self.S[9] | self.S[10] | self.S[16] | self.S[17] | self.S[18] | self.S[24] | self.S[25] | self.S[26]
		self.MASK_R5 = self.S[5] | self.S[6] | self.S[7] | self.S[13] | self.S[14] | self.S[15] | self.S[21] | self.S[22] | self.S[23] | self.S[29]  | self.S[30]  | self.S[31]

	@property
	def name(self):
		return self._name

	@property
	def desc(self):
		return self._desc
	
	

	def selectMove(self):
		self.convert2BB()

		# pick random move any way
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moveList[moveNo]

	"""
	Identify which pieces on move have a valid non-jump move
	Square 0 is in the upper left corner.
	Empty spaces in front of the red pieces are right shifted
	to check the diagonal square for a red piece
	Kings need to check in both directions
	"""
	def getMovers( self ):
		s = self.board.onMove

		onMove = self.bp if s == 1 else self.rp
		forShift = operator.rshift if s == 1 else operator.lshift 
		bacShift = operator.lshift if s == 1 else operator.rshift
		forMsk3 = self.MASK_R3 if s == 1 else self.MASK_L3
		forMsk5 = self.MASK_R5 if s == 1 else self.MASK_L5
		kgMsk3 = self.MASK_L3 if s == 1 else self.MASK_R3
		kgMsk5 = self.MASK_L5 if s == 1 else self.MASK_R5
		
		K = onMove & self.k
		empty = self.emptySqs

		movers =  forShift( empty, 4 ) & onMove
		movers |= forShift( empty & forMsk3, 3 ) & onMove
		movers |= forShift( empty & forMsk5, 5 ) & onMove
		if ( K ):
			movers |= bacShift( empty, 4 ) & onMove
			movers |= bacShift( empty & kgMsk3, 3 ) & onMove
			movers |= bacShift( empty & kgMsk5, 5 ) & onMove
		return movers

	def convert2BB( self ):
		position = self.board.position
		i = 0
		for x, row in enumerate(position):
			for y, sq in enumerate(row):
				# only set the dark squares
				# dark squares are when row and column numbers are not both even
				if ( x%2 != y%2 ):
					self.setSq( sq, i )
					i+=1
		# No we can extract other useful information
		# Empty Squares
		self.emptySqs = np.uint32(~(self.rp | self.bp ))

	def setSq( self, sq, i ):
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

	"""
	Set single bit in binary word
	n binary number
	p int position to be changed starting at 0
	b int new value of bit, 1 or 0
	from https://www.geeksforgeeks.org/modify-bit-given-position/
	"""
	def modifyBit( self, n,  p,  b):
		mask = 1 << p 
		return (n & ~mask) | ((b << p) & mask)

	# Count the number of bits set.
	# From https://www.geeksforgeeks.org/count-set-bits-in-an-integer/
	def countSetBits(self, n):
	    return (bin(n).count('1'))