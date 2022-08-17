from board2 import Board
import engines

from positions import positions

sides = {1 : "Black", -1 : "White"}

def make_move(board, engine):
	move = engine.selectMove()
	board.makeMove(move)
	print(getEngineInfo(engine, move))

def debug(pos, board, engine):
	print(f"{engine.name} to move as {sides[board.onMove]}.")
	print("Thinking...", end='\r')
	make_move(board, engine)
	print(board.printBoard())

def getEngineInfo(engine, move):
	return f"{engine.name} - {sides[-engine.board.onMove]}'s Move: {move}; Score: {engine.score}; Time: {engine.elapsedTime}; Nodes: {engine.totalNodes}; nps: {engine.nps})"


pos = '[FEN "W:WK3:BK7,K26"]'
b = Board(pos)
debug(pos, b, engines.minmaxB(b, maxdepth=5))


'''
Positions I find interesting:
'[FEN "W:W31,32,25,27,28,21,22,23,K1:B15,16,9,5,7,4"]'
! Wow. The current board is a +4 for white. Minmax has 9 legal moves. 
7 moves are safe. (One, 22 to 18, is a disaster for white.) 
But, minmax comes up with 23-19, sacrificing a piece. Moron can take in 
2 ways. Either way, minmax correctly calculates gaining 3 points, picking up
3 pieces in exchange for 1 and getting a king, a +3 advantage.
MinMaxA@d3, [23, 19], 7, [FEN "W:W31,32,25,27,28,21,22,23,K1:B15,16,9,5,7,4"]
  W   -   -   b   
b   -   b   -   
  b   -   -   -   
-   -   b   b   
  -   -   -   -   
w   w   w   -   
  w   -   w   w   
-   -   w   w   
**************


'[FEN "B:W17,21,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,10,11,12,14"]'
in this position, minmax5 moved from 14 to 18, ensuring a capture without compensation. Originally, I thought this was a problem with evaluation. But on futher reflection, at depth 5 cannot see the final jump that will give white the lead. After [14-18], [23 - 18], [6 - 9] and it looks like b will get the piece back. But not until after [26 - 23] is it obvious that b loses a piece permanently.

At depth 7 b sees over the horizon and makes a different move.
  b   b   b   b
b   b   b   b
  -   b   b   b
-   b   -   -
  w   -   -   -
w   -   w   w
  w   w   w   w
w   w   w   w
**************
'''
