import copy
import math
import operator
import random
import re
from types import SimpleNamespace
import time
from engines.engine import Engine
from engines.moveNode import littleBNode as moveNode
from board2 import Board
from positions import positions
'''
littleBitB: Modified littleBitA using a different bitboard pattern
Translate board position to a bit board 
Glen Pritchard -- 9/8/2022
'''
class player(Engine):
	def __init__(self, board, maxdepth=2, ab=False, maketree=False):
		super(player, self).__init__(board)
		self._name = "littleBitB"
		self._desc = "littleBitA with different bitboard pattern"
		self.maxdepth = maxdepth
		self.ab = ab
		self.maketree = maketree
		self.totalNodes = 0
		# all squres and padding
		self.S = tuple(2 ** i for i in range(36))
		# legal squares (not including the padding) 
		self.legalSquares = tuple(2 ** i for i in range(36) if i not in(8, 17, 26, 35))
		# bitpos2fen maps bit positions to fen square numbers
		legalSqPositions = tuple(i for i in range(36) if i not in (8,17,26,35))
		self.bitpos2fen = {v: i+1 for i, v in enumerate(legalSqPositions)}
		# mask for the padding squares [8, 17, 26, 35, 36, 37, 38, 39]
		self.padding = 1065219129600
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
	
	@property
	def name(self):
		return f"{self._name}@d{self.maxdepth}"

	def selectMove(self, position = None, moves = None):
		self.totalNodes = 0
		startTime = time.time()
		moves = self.getMoves()
		self.root = moveNode(self.getBoardStr, [None, self.convPos2BB(self.board.pos2Fen())]) if self.maketree else None
		score, move = self.negaMax(moves, 0, -1, parentNode=self.root)
		endTime = time.time()
		self.elapsedTime = round(endTime - startTime, 2)
		try:
			self.nps = int(self.totalNodes/self.elapsedTime)
		except ZeroDivisionError:
			self.nps = "0 Error"
		self.score = score
		if move:
			fenmove = self.move2FEN(move[0])
		else:
			fenmove = None
		return fenmove

	def move2FEN(self, move):
		retval = []
		for i in move:
			try:
				retval.append(self.bitpos2fen[i])
			except:
				breakpoint()
		return retval

	def getMoves(self, position = None):
		if position == None:
			position = self.convPos2BB(self.board.pos2Fen())
		jumpers = self.getJumpers(position)
		if jumpers:
			moves = self.getJumpMoves(position, jumpers)
		else:
			movers = self.getMovers(position)
			if movers:
				moves = self.getNormalMoves(position, movers)
			else:
				return None
		return moves

	def negaMax(self, position, depth, maxplayer, tmove=[], alpha=None, beta=None, parentNode=None):
		'''
		Find minmax's best move recursively until self.maxdepth of the search tree
		@param position: list: [a, b, c, d] where:
			a: black man bitboard
			b: white man bitboard
			c: king bitboard
			d: side to move, 1 for black; -1 for white
		@param depth: int: maximum depth of search
		@param maxplayer: int: whether to maximize or minimize, 1 to minimize; -1 to maximize
		@param alpha: float:
		@param beta: float:
		'''
		v = float('inf') * maxplayer
		# if depth, then return evaluation and the move
		if self.maxdepth == depth:
			return self.scorePosition(tmove), None
		# if there are no moves in this position, game over
		elif position == None or position == []:
			return 100*maxplayer, None
		# iterate moves from position
		else:
			for move in position:
				tempv = v
				if parentNode:
					node = moveNode(self.getBoardStr, move)
					parentNode.addChild(node)
					node.move = self.move2FEN(move[0])
				else:
					node = None
				self.totalNodes += 1
				v, placeholder = self.negaMax(
					self.getMoves(move[1]), 
					depth+1, 
					-maxplayer,
					move,
					alpha, 
					beta,
					node)
				if maxplayer == -1:
					if v > tempv:
						best_move = move
					v = max(v, tempv)
				else:
					v = min(v, tempv)
					best_move = None
			return v, best_move

	def scorePosition(self, position):
		pos = position[1]
		bpCount = self.countSetBits(pos[0])
		bpCount += self.countSetBits(pos[0] & pos[2])
		if bpCount == 0:
			return -100 if pos[3] == 1 else 100
		wpCount = self.countSetBits(pos[1])
		wpCount += self.countSetBits(pos[1] & pos[2])
		if wpCount == 0:
			return 100 if pos[3] == 1 else -100
		score = bpCount - wpCount
		if pos[3] == 1:
			return score
		else:
			return -score

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
				movers |= (empty >> 4 & kings) | (empty >> 5 & kings)
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
			if kings & friend:
				temp = empty >> 4 & enemy 
				jumpers |= temp >> 4 & (kings & friend) 
				temp = empty >> 5 & enemy 
				jumpers |= temp >> 5 & (kings & friend)
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
					lsop = operator.mul if shift[1]>0 else operator.floordiv 
					landingSq = lsop(val, 2**abs(shift[1]))
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
						if landingSq & ~newkings:
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
		print(self.getBoardStr(data))

	def getBoardStr(self, data):
		"""
		Print bitboard as human readable board
		@ param data: int or list: if list of 4 ints, the current position 
		is displayed as pieces (b, r, B, R). 
		Assuming list is [bp, rp, kings, onmove]
		If int, the bitWord is displayed as 0s and 1s
		"""
		sq = 0
		spacer = "  "
		topBottom = "   -------------------\n"
		output = topBottom
		borderNums = (0, 3, 4, 7, 9, 12, 13, 16, 18, 21, 22, 25, 27, 30, 31, 34)
		i = 0
		for row in range(8):
			s = spacer if row%2 == 0 else ""
			s = "{:>2} | ".format(borderNums[i])+s
			for col in range(4):
				mask = 1 << sq
				if mask & self.padding:
					mask = mask << 1
					sq+=1
				if( type(data) == list ):
					if( data[0] & mask ): s += 'b '
					elif( data[1] & mask ):	s += 'w '
					else: s += "- "
					if( data[2] & mask ): s = s.upper()
				else:
					if( data & mask ): s += '1'
					else: s +='0'
				sq += 1
				s += spacer
			s = s.rstrip()
			output += s.ljust(20, " ")+" | {:>2}\n".format(borderNums[i+1])
			i+=2
		return output + topBottom

if __name__ == '__main__':
	# pos = positions['multiJumpA']
	# pos = positions['royalTour']
	# pos = positions['jump']
	# pos = positions['kingJump']
	# pos = '[FEN "W:W11:BK7"]'
	# pos = '[FEN "B:W18,26,27,25,11,19:B15"]'
	# pos = '[FEN "B:W22,30:BK18"]' #Not working. Tries to jump 30 off the board
	# pos = '[FEN "W:W15:B10,1"]' #But this does work. w does not try to jump 1
	# pos = '[FEN "B:W15:BK30"]' # Not working tries to move off board to 36
	royalTour = [
	    '[FEN "W:W27,19,18,11,7,6,5:B28,26,25,20,17,10,9,4,3,2"]', #14, 0
	    '[FEN "B:W27,18,15,11,5,6,7:B25,26,28,17,20,9,10,2,3,4"]', #13, 1
	    '[FEN "W:W27,18,11,5,6,7:B25,26,28,17,19,20,9,2,3,4"]', #12, 2
	    '[FEN "B:W27,18,11,6,7,K1:B25,26,28,17,19,20,9,2,3,4"]', #11, 3
	    '[FEN "W:W27,18,11,6,K1:B25,26,28,17,19,20,9,10,2,4"]', #10, 4
	    '[FEN "B:W27,18,6,8,K1:B25,26,28,17,19,20,9,10,2,4"]', #9, 5
	    '[FEN "W:W27,18,6,K1:B25,26,28,17,19,20,9,10,11,2"]', #8, 6
	    '[FEN "B:W24,18,6,K1:B25,26,28,17,19,20,9,10,11,2"]', #7, 7
	    '[FEN "W:W18,6,K1:B25,26,27,28,17,19,9,10,11,2"]', #6, 8
	    '[FEN "B:W14,6,K1:B25,26,27,28,17,19,9,10,11,2"]', #5, 9
	    '[FEN "W:W6,K1:B25,26,27,28,17,18,19,10,11,2"]', #4, 10
	    '[FEN "B:WK5,6:B25,26,27,28,17,18,19,10,11,2"]', #3, 11
	    '[FEN "W:WK5:B25,26,27,28,17,18,19,9,10,11"]', #2, 12
	    '[FEN "B:WK32:B28"]' #1, 13
	]
	pos = '[FEN "W:W18,6,K1:B25,26,27,28,17,19,9,10,11,2"]'
	b = Board(pos)
	print(b.printBoard())
	# b.onMove = -b.onMove
	p = player(b, maxdepth=6)
	move = p.selectMove()
	print(move, p.score)