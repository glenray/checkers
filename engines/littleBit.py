import random
import re
import operator
import numpy as np
from engines.engine import Engine
from types import SimpleNamespace
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
		self._desc = "I translate the position into a bit board, but moves are random."
		self.bp = np.uint32(0)
		self.rp = np.uint32(0)
		self.k =  np.uint32(0)
		self.emptySqs = np.uint32(0)
		self.S = []
		self.S.append(1)
		for  i in range(1, 32):
			self.S.append( np.uint32(self.S[i-1] * 2) )
		# These left shift and right shift masks work when square 0 is on the top left
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

	"""
	Identify which pieces on move have a valid non-jump move
	Square 0 is in the upper left corner.
	Empty spaces in front of the red pieces are right shifted
	to check the diagonal square for a red piece
	Kings need to check in both directions
	"""
	def getMovers( self ):
		n = self.getSideVars()		

		movers =  n.forShift( self.emptySqs, 4 ) & n.onMove
		movers |= n.forShift( self.emptySqs & n.forMsk3, 3 ) & n.onMove
		movers |= n.forShift( self.emptySqs & n.forMsk5, 5 ) & n.onMove
		if n.K:
			movers |= n.bacShift( self.emptySqs, 4 ) & n.onMove
			movers |= n.bacShift( self.emptySqs & n.kgMsk3, 3 ) & n.K
			movers |= n.bacShift( self.emptySqs & n.kgMsk5, 5 ) & n.K
		return movers

	# return pieces that can jump
	def getJumpers( self ):
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

	# set side of board variables
	# depending on color, sets the direction of forward and backward moves
	def getSideVars( self ):
		s = self.board.onMove
		d = {
			'onMove' : self.bp if s == 1 else self.rp,
			'enemy' : self.rp if s == 1 else self.bp,
			'forShift' : operator.rshift if s == 1 else operator.lshift,
			'bacShift' : operator.lshift if s == 1 else operator.rshift,
			'forMsk3' : self.MASK_R3 if s == 1 else self.MASK_L3,
			'forMsk5' : self.MASK_R5 if s == 1 else self.MASK_L5,
			'kgMsk3' : self.MASK_L3 if s == 1 else self.MASK_R3,
			'kgMsk5' : self.MASK_L5 if s == 1 else self.MASK_R5,
		}
		d['K'] = d['onMove'] & self.k

		return SimpleNamespace(**d)

	# create bit board representation from board.position 8x8 array
	def convert2BB( self, position ):
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


				
		# i = 0
		# for x, row in enumerate(position):
		# 	for y, sq in enumerate(row):
		# 		# only set the dark squares
		# 		# dark squares are when row and column numbers are not both even or both odd
		# 		if ( x%2 != y%2 ):
		# 			self.setSq( sq, i )
		# 			i+=1

		# Now we can extract other useful information
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