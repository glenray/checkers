"""
Methods used for debugging bit board engines
Glen Pritchard 6-16-2019
"""
class debug():
	def prBinary ( self, bword ):
		return bin( bword )[2:].rjust(32, '0')

	"""
	Display bitboard as human readable board
	@ isBoard bool if true displays the current position as pieces 
	b, r, B, R, else just print 1 and 0s. Otherwise, shows the bitWord as 0s and 1s
	"""
	def printBoard(self, eng, bitWord=None):
		sq = 0
		spacer = "  "
		output = ""
		for row in range(8):
			s = spacer 	if row%2 == 0 else ""
			for col in range(4):
				mask = 1 << sq
				if( bitWord == None ):
					if( eng.bp & mask > 0 ): s += 'b'
					elif( eng.rp & mask > 0 ):	s += 'r'
					else: s += "-"

					if( eng.k & mask > 0 ): s = s.upper()
				else:
					if( bitWord & mask>0 ): s += '1'
					else: s +='0'

				sq += 1
				output += s+spacer
				s=""
			output += "\n"
		return output
