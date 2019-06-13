import random
import time
import numpy as np
'''
littleBit: Translate board position to a bit board 
Does not select any move yet
Glen Pritchard -- 6/5/2019

A good tutorial about bitboards for checkers:
https://www.3dkingdoms.com/checkers/bitboards.htm
'''
class player():
	def __init__(self, board):
		self.board = board
		self.name = "littleBit"
		self.desc = "I translate the position into a bit board. No move selection yet."
		self.bp = np.uint32(0)
		self.rp = np.uint32(0)
		self.k =  np.uint32(0)
		self.emptySqs = np.uint32(0)
		self.S = []
		self.S.append(1)
		for  i in range(1, 32):
			self.S.append( self.S[i-1] * 2 )
		# This mask work when square 0 is on the top left
		self.MASK_R3 = self.S[5] | self.S[6] | self.S[7] | self.S[13] | self.S[14] | self.S[15] | self.S[21] | self.S[22] | self.S[23]
		self.MASK_R5 = self.S[0] | self.S[1] | self.S[2] | self.S[8] | self.S[9] | self.S[10] | self.S[16] | self.S[17] | self.S[18] | self.S[24]  | self.S[25]  | self.S[26]
		self.MASK_L3 = self.S[8] | self.S[9] | self.S[10] | self.S[16] | self.S[17] | self.S[18] | self.S[24] | self.S[25] | self.S[26]
		self.MASK_L5 = self.S[5] | self.S[6] | self.S[7] | self.S[13] | self.S[14] | self.S[15] | self.S[21] | self.S[22] | self.S[23] | self.S[29]  | self.S[30]  | self.S[31]

	def selectMove(self):
		self.convert2BB()
		self.printBoard()
		self.printBoard(self.getMoversBlack())
		# exit()

		# pick random move any way
		self.board.getLegalMoves()
		moveList = self.board.legalMoves
		moveLen = len(moveList)
		if moveLen > 0:
			moveNo = random.randint(0, moveLen-1)
			return moveList[moveNo]

	def getMovers(self, side=None):
		onMove = 1

	# to combine these functions, see https://stackoverflow.com/questions/2983139/assign-operator-to-variable-in-python
	def getMoversBlack( self ):
		BK = self.bp & self.k
		movers = ( self.emptySqs >> 4 ) & self.bp
		movers |= ( ( self.emptySqs & self.MASK_L3 ) >> 3 ) & self.bp
		movers |= ( ( self.emptySqs & self.MASK_L5 ) >> 5 ) & self.bp
		if( BK ):
			movers |= (self.emptySqs << 4 ) & BK
			movers |= (( self.emptySqs & self.MASK_R3 ) << 3 )
			movers |= (( self.emptySqs & self.MASK_R5 ) << 5 )
		return movers

	def getMoversRed( self ):
		RK = self.rp & self.k
		movers = ( self.emptySqs << 4 ) & self.rp
		movers |= ( ( self.emptySqs & self.MASK_L3 ) << 3 ) & self.rp
		movers |= ( ( self.emptySqs & self.MASK_L5 ) << 5 ) & self.rp
		if( RK ):
			movers |= (self.emptySqs >> 4 ) & RK
			movers |= (( self.emptySqs & self.MASK_R3 ) >> 3 )
			movers |= (( self.emptySqs & self.MASK_R5 ) >> 5 )
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

	def prBinary ( self, bword ):
		print(bin( bword )[2:].rjust(32, '0'))

	def prPos( self ):
		print(bin(self.bp)[2:].rjust(32,'0'))
		print(bin(self.rp)[2:].rjust(32,'0'))
		print(bin(self.k)[2:].rjust(32,'0'))
		print("\n")

	def setSq( self, sq, i ):
		if sq == 0:
			bpBit = 0
			rpBit = 0
			kBit  = 0
		else:
			bpBit = 1 if sq < 3 else 0
			rpBit = 1 if sq > 2 else 0
			kBit  = 1 if sq % 2 == 0 else 0

		self.bp = self.modifyBit( self.bp, i, bpBit)
		self.rp = self.modifyBit( self.rp, i, rpBit)
		self.k = self.modifyBit( self.k, i, kBit)

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

	"""
	Display bitboard as human readable board
	@ isBoard bool if true displays the current position as pieces 
	b, r, B, R, else just print 1 and 0s. Otherwise, shows the bitWord as 0s and 1s
	"""
	def printBoard(self, bitWord=None):
		sq = 0
		spacer = "  "
		for row in range(8):
			output = ""
			s = spacer 	if row%2 == 0 else ""
			for col in range(4):
				mask = 1 << sq
				if( bitWord == None ):
					if( self.bp & mask > 0 ): s += 'b'
					elif( self.rp & mask > 0 ):	s += 'r'
					else: s += "-"

					if( self.k & mask > 0 ): s = s.upper()
				else:
					if( bitWord & mask>0 ): s += '1'
					else: s +='0'

				sq += 1
				output += s+spacer
				s=""
			print(output)
		# extra line at end of board
		print("\n")

	# Count the number of bits set.
	# From https://www.geeksforgeeks.org/count-set-bits-in-an-integer/
	def countSetBits(self, n):
	    return (bin(n).count('1'))

	def __repr__(self):
		return "%s: %s" % (self.name, self.desc)