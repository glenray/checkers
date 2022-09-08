import math
import operator
import random
import re
from types import SimpleNamespace
from engines.engine import Engine
from board2 import Board
from positions import positions
'''
littleBitB: Modified littleBitA using a different bitboard pattern
Translate board position to a bit board 
Glen Pritchard -- 9/8/2022
'''
class player(Engine):
	def __init__(self, board):
		super(player, self).__init__(board)
		self._name = "littleBitB"
		self._desc = "littleBitA with different bitboard pattern"
		self.sideVars = None
		# legal squares (not including the padding) 
		self.S = tuple(2 ** i for i in range(36) if i not in(8, 17, 26, 35))
		# mask for the padding squares
		self.padding = 34426978560
		"""
		-- All squares work with shift 4 or 5.
		-- This is the primary benefit over littleBitA arrangement.
		-- bits 8, 17, 26, and 35 are padding (not legal squares)
		to keep everything in line.
		__________________________
		|   000   001   002   003|
		|004   005   006   007   | 008
		|   009   010   011   012|
		|013   014   015   016   | 017
		|   018   019   020   021|
		|022   023   024   025   | 026
		|   027   028   029   030|
		|031   032   033   034   | 035
		--------------------------
		"""
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
		@param position: list: position [bp, rp, k, onMove] to look for movers
		@return int: bitboard of movers
		"""
		movers = 0
		friend = position[0] if position[3] == 1 else position[1]
		enemy = position[1] if position[3] == 1 else position[0]
		empty = self.emptySqs(position)
		kings = position[2]
		if position[3] == 1:
			movers = (empty >> 4 & friend) | (empty >> 5 & friend)
			if kings:
				movers |= (empty << 4 & kings) | (empty << 5 & kings)
		else:
			movers = (empty << 4 & friend) | (empty << 5 & friend)
			if kings:
				movers = (empty >> 4 & kings) | (empty >> 5 & kings)
		return movers

	def getJumpers(self, position):
		'''
		Return a bitboard of pieces that can jump.
		@param position: list: position to look for jumpers [bp, rp, k, onMove]
		@return int: bitboard of jumpers
		'''
		jumpers = 0
		friend = position[0] if position[3] == 1 else position[1]
		enemy = position[1] if position[3] == 1 else position[0]
		empty = self.emptySqs(position)
		if position[3] == 1:
			temp = empty >> 4 & enemy 
			jumpers |= temp >> 4 & friend 
			temp = empty >> 5 & enemy 
			jumpers |= (temp >> 5 & friend)
		else:
			temp = empty << 4 & enemy 
			jumpers |= temp << 4 & friend 
			temp = empty << 5 & enemy 
			jumpers |= (temp << 5 & friend)
		return jumpers

	def initSideVars (self):
		black = {
			'forShift' 	: operator.rshift,
			'bacShift' 	: operator.lshift,
		}
		white = {
			'forShift' 	: operator.lshift,
			'bacShift' 	: operator.rshift,
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

	def convPos2BB(self, fen=None):
		'''
		Convert board2.Board FEN string to bitboards
		@return list: a list of 4 ints consisting of: 
		0: bp (bit board of black pieces), 
		1: rp (bitboard of red pieces), 
		2: kings (bitboard of kings),
		3: side on move (1 for black, -1 for white)
		'''
		position  = [0, 0, 0, 0]
		fenpos = self.board.pos2Fen() if fen==None else fen
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
				# self.setSq(position, pColor, int(sq)-1)
				if pColor < 3:
					position[0] += self.S[int(sq)-1]
				if pColor > 2:
					position[1] += self.S[int(sq)-1]
				if pColor % 2 == 0:
					position[2] += self.S[int(sq)-1]
		return position

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
		@return str: 36 character representation of bitboard
		'''
		return bin(bitboard)[2:].rjust(36, '0')

	def emptySqs(self, position):
		'''
		Return bitboard of empty squares in position
		@param tuple: position in the form (bp, wp, k, side2move)
		@return int: bitboard of empty squares
		'''
		return ~(self.padding | position[0] | position[1])

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
		pass
		# n = self.getSideVars(position)

	def getJumpMoves(self, position, jumpers):
		pass

	def jumpersRecurse(self, js, moves, position, sideVars):
		pass

	def printBoard(self, data):
		"""
		Display bitboard as human readable board
		@ param data: int or list: if list of 4 ints, the current position 
		is displayed as pieces (b, r, B, R). 
		Assuming list is [bp, rp, kings, onmove]
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
				if mask & self.padding:
					mask = mask << 1
					sq+=1
				if( type(data) == list ):
					if( data[0] & mask ): s += 'b'
					elif( data[1] & mask ):	s += 'r'
					else: s += "-"
					if( data[2] & mask ): s = s.upper()
				else:
					if( data & mask ): s += '1'
					else: s +='0'
				sq += 1
				output += s+spacer
				s=""
			output += "\n"
		return output

if __name__ == '__main__':
	pos = positions['multiJumpA']
	# pos = positions['jump']
	# pos = positions['kingJump']
	b = Board(pos)
	# b.onMove = -1
	p = player(b)
	position = p.convPos2BB()
	movers = p.getMovers(position)
	jumpers = p.getJumpers(position)
	print(b.printBoard())
	print(p.printBoard(movers), '\n')
	print(p.printBoard(jumpers), '\n')