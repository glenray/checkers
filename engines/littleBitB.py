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
		# all squres and padding
		self.S = tuple(2 ** i for i in range(36))
		# legal squares (not including the padding) 
		self.legalSquares = tuple(2 ** i for i in range(36) if i not in(8, 17, 26, 35))
		# mask for the padding squares
		self.padding = 34426978560
		self.blk_king_row_mask = self.S[31] | self.S[32] | self.S[33] | self.S[34]
		self.wht_king_row_mask = self.S[0] | self.S[1] | self.S[2] | self.S[3]
		self.jumps = []
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
	
	def selectMove(self, position = None, moves = None):
		bbPos = self.convPos2BB(self.board.pos2Fen())
		jumpers = self.getJumpers(bbPos)
		if jumpers:
			moves = self.getJumpMoves(bbPos, jumpers)
		else:
			movers = self.getMovers(bbPos)
			if movers:
				moves = self.getNormalMoves(bbPos, movers)
			else:
				print("No moves, game over.")
		return moves

	def negaMax(self, position, depth, mp):
		pass

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
		# black to move
		if position[3] == 1:
			# line up empty squares and black squares
			movers = (empty >> 4 & friend) | (empty >> 5 & friend)
			if kings & friend:
				movers |= (empty << 4 & kings) | (empty << 5 & kings)
		else:
			movers = (empty << 4 & friend) | (empty << 5 & friend)
			if kings & friend:
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
		kings = position[2]
		empty = self.emptySqs(position)
		# Black to move
		if position[3] == 1:
			temp = empty >> 4 & enemy 
			jumpers |= temp >> 4 & friend 
			temp = empty >> 5 & enemy 
			jumpers |= (temp >> 5 & friend)
			if kings:
				temp = empty << 4 & enemy 
				jumpers |= temp << 4 & kings 
				temp = empty << 5 & enemy 
				jumpers |= temp << 5 & kings
		# White to move
		else:
			temp = empty << 4 & enemy 
			jumpers |= temp << 4 & friend 
			temp = empty << 5 & enemy 
			jumpers |= (temp << 5 & friend)
			if kings:
				temp = empty >> 4 & enemy 
				jumpers |= temp >> 4 & friend 
				temp = empty >> 5 & enemy 
				jumpers |= (temp >> 5 & friend)
		return jumpers

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
					position[0] += self.legalSquares[int(sq)-1]
				if pColor > 2:
					position[1] += self.legalSquares[int(sq)-1]
				if pColor % 2 == 0:
					position[2] += self.legalSquares[int(sq)-1]
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
		Get non-jump moves and the resulting position
		from a bit board of movers
		@ param position: list: [a, b, c, d] where:
			a: black piece bit board
			b: white piece bit board
			c: king bit board
			d: side to move, 1 = black; -1 = white
		@ param movers: bin: bit board of non jump movers
		@ return None
		Appends to self.moves a tuple(a,b) where:
			a: list of tuples (x, y), where x is the starting
			positional bit of the piece and y is the landing square.
			b: list: the position resulting from the move in the same
			format as the position param described above
		'''
		moves = []
		empty = self.emptySqs(position)
		kings = position[2]
		onMove = position[3]
		move_operator = operator.lshift if onMove == 1 else operator.rshift
		friend = position[0] if onMove == 1 else position[1]
		enemy = position[1] if onMove == 1 else position[0]
		men_shift = (
			(empty >> 4 if onMove == 1 else empty << 4, 4*onMove),
			(empty >> 5 if onMove == 1 else empty << 5, 5*onMove),
		)
		king_shift = (
			(empty << 4 if onMove == 1 else empty >> 4, -4*onMove),
			(empty << 5 if onMove == 1 else empty >> 5, -5*onMove),	
		)
		while movers:
			x = self.getFirstSetBitPosition(movers)
			val = 2 ** x
			shiftVar = men_shift+king_shift if (val & kings) else men_shift
			for shift in shiftVar:
				newkings = kings
				if val & shift[0]:
					landingSq = move_operator(val, abs(shift[1]))
					# toggle from bit
					newfriend = friend ^ val
					# toggle landing bit
					newfriend = newfriend ^ landingSq
					# update king bitboard
					if val & kings:
						newkings = newkings ^ val
						newkings = newkings ^ landingSq
					# king promotion
					if (landingSq & self.wht_king_row_mask) | (landingSq & self.blk_king_row_mask):
						# mover is not already a king
						if landingSq & ~kings:
							newkings += landingSq
					new_position = [
						newfriend if onMove == 1 else enemy,
						newfriend if onMove == -1 else enemy,
						newkings if newkings else kings,
						-onMove
					]
					moves.append(([x, x+shift[1]], new_position))
			# is this the fastest way?
			movers -= val
		return moves

	def getJumpMoves(self, position, jumpers):
		moves = []
		self.jumps = []
		while jumpers:
			x = self.getFirstSetBitPosition(jumpers)
			val_x = 2 ** x
			moves.append(self.jumperRecurse(x, val_x, position))
			jumpers -= val_x
		return self.jumps

	def jumperRecurse(self, jumper, jumperBB, position, jumps=[]):
		empty = self.emptySqs(position)
		kings = position[2]
		onMove = position[3]
		newMoves = None
		islastMove = False
		# set side dependent variables
		if onMove == 1:
			friend = position[0]
			enemy = position[1]
			menShift = operator.rshift 
			kingShift = operator.lshift 
		else:
			friend = position[1]
			enemy = position[0]
			menShift = operator.lshift 
			kingShift = operator.rshift 
		men_vars = [
			((menShift((menShift(empty, 4) & enemy), 4) & jumperBB), 4*onMove), 
			((menShift((menShift(empty, 5) & enemy), 5) & jumperBB), 5*onMove),
		]
		king_vars = [
			((kingShift((kingShift(empty, 4) & enemy), 4) & jumperBB), -4*onMove), 
			((kingShift((kingShift(empty, 5) & enemy), 5) & jumperBB), -5*onMove),
		]
		variations = men_vars + king_vars if jumperBB & kings else men_vars
		for var in variations:
			if var[0]:
				shiftVal = var[1]
				landingSq = 2 ** (jumper+(shiftVal*2))
				jumpedSq = 2 ** (jumper+shiftVal)
				newMoves = [jumper, jumper + (shiftVal*2)] if jumps==[] else jumps+[jumper+(shiftVal*2)]
				newFriend = friend - jumperBB + landingSq
				newEnemy = enemy - jumpedSq 
				newKings = kings
				# If the jumper is a king, subtract it from where it was and add it to where it landed
				if jumperBB & kings:
					newKings = newKings-jumperBB+landingSq
				# if the jumped piece is a king, subtract it from where it was
				if kings & jumpedSq:
					newKings = newKings - jumpedSq
				# if landing square is back row
				if (landingSq & self.blk_king_row_mask) | (landingSq & self.wht_king_row_mask):
					# if jumper was not a king, make it one and then finish this branch since the new king cannot continue to jump.
					if landingSq & ~newKings:
						newKings = newKings + landingSq
						newPosition = [newFriend, newEnemy, newKings, -position[3]] if onMove == 1 else [newEnemy, newFriend, newKings, -position[3]]
						self.jumps.append((newMoves, newPosition))
						continue	
				# the new position after the jump with the same side to move before looking for another jump in the same move
				newPosition = [newFriend, newEnemy, newKings, position[3]] if onMove == 1 else [newEnemy, newFriend, newKings, position[3]]
				self.jumperRecurse(jumper+(shiftVal*2), landingSq, newPosition, newMoves)
		if newMoves == None and jumps:
			# toogle onMove
			position[3] = -position[3]
			self.jumps.append((jumps, position))

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
					elif( data[1] & mask ):	s += 'w'
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
	# pos = positions['multiJumpA']
	pos = positions['royalTour']
	# pos = positions['jump']
	# pos = positions['kingJump']
	# pos = '[FEN "W:W11:BK7"]'
	# pos = '[FEN "B:W18,26,27,25,11,19:B15"]'
	b = Board(pos)
	b.onMove = -b.onMove
	p = player(b)
	moves = p.selectMove()
	print(b.printBoard())
	for move in moves:
		print(f'Move: {move[0]}')
		print(p.printBoard(move[1]))
