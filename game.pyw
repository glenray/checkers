from board import Board
from GUI import GUI
from engines.moron import player as moron
from engines.snap import player as snap

positions = {
	"normalStart"	: '[FEN "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"]',
	"jump"			: '[FEN "B:W18,19,10:B15K"]',
	"one"			: '[FEN "W:W21K,25K:B9K,10,11,12"]',
	"multiJumpA"	: '[FEN "B:W18,26,27,25,11,19:B15K"]',
	"multiJumpB"	: '[FEN "B:W18,26,27,25,11,19:B15K,14K"]',
	"kingJump"		: '[FEN "B:W17,26,25:B23"]',
}
b = Board(positions['normalStart'])
a = GUI(b)