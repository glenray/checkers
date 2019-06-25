import re

"""
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
		self.OOB 		= -1  # out of bounds value
		self.EMPTY 		= 0
		self.BP 		= 1
		self.BK 		= 2
		self.RP 		= 3
		self.RK 		= 4
		self.onMove		= None
		self.position 	= {}
		self.startPos = startPos if startPos != None else '[FEN "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"]'
		
		# init empty position
		for sq in range(0, 46):
			if sq in [0,1,2,3,4,9,18,27,36,41,42,43,44,45]:
				self.position[sq] = self.OOB
			else:
				self.position[sq] = self.EMPTY

	
	def printBoard(self):
		offset = "  "
		for start in [37, 32, 28, 23, 19, 14, 10, 5]:
			output = ''
			for row in range(0,4):
				output += str(self.position[start+row])+"   "
			print(offset, output)
			offset = '' if offset == "  " else "  "


	def parseFen(self, position=None):
		FEN2Pos = dict([(1,37), (2,38), (3,39), (4,40), (5,32), (6,33), (7,34), (8,35), (9,28), (10,29), (11,30), (12,31), (13, 23), (14, 24), (15, 25), (16, 26), (17, 19), (18, 20), (19, 21), (20, 22), (21, 14), (22, 15), (23, 16), (24, 17), (25, 10), (26, 11), (27, 12), (28, 13), (29, 5), (30, 6), (31, 7), (32, 8)])

		if position==None:
			position = self.startPos

		position = re.findall(r'"([^"]*)"', position)
		sides = position[0].split(':')
		self.onMove = 1 if sides[0] == 'B' else -1
		pieces = {
			"white": (sides[1][1:] if sides[1].startswith('W') else sides[1]).split(','),
			"black": (sides[2][1:] if sides[2].startswith('B') else sides[2]).split(',')
		}
		
		for color in pieces:
			for sq in pieces[color]:
				pColor = self.BP if color == 'black' else self.RP
				pColor = pColor+1 if sq[:2] == 'K' else pColor
				self.position[FEN2Pos[sq]] = pColor

		self.printBoard()


if __name__ == "__main__" :
	a = Board()
	a.parseFen()
