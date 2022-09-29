import tkinter as tk
import tkinter.ttk as ttk
import time
import board2
import engines
from sqCanvas import sqCanvas

class GUI:
	# The odd row FEN squares used to calculate jumped squares.
	ODD_ROW_SQUARES = (5,6,7,8,13,14,15,16,21,22,23,24,29,30,31,32)

	def __init__(self, board, bp='human', wp='human'):
		'''
		@param board: board2.Board object
		@param bp: str or engine object: "human" to let human play the
		black side or an engine instance
		@param wp: str or engine object: "human" to let human play the
		white side or an engine instance
		'''
		self.board = board
		self.bp = bp
		self.wp = wp
		self.boardSize = 400
		self.lightColorSq = "yellow"
		self.darkColorSq = "blue"
		self.litSqColor = "green"
		self.squares = []		# list of ids for canvas rectangles
		self.darkSquares = []	# list of ids for dark squares
		self.sqLabels = []		# list of ids for dark square number labels
		self.MiP = None			# for human moves in progress
		self.isRunning = True

		self.createWidgets()
		self.createCanvasObjects()
		self.positionCanvasObjects()
		self.drawPieces()
		self.makeMove()	
		self.root.mainloop()


	def createWidgets(self):
		# The window
		self.root = tk.Tk()
		self.root.title("Glen's Checkers")
		self.root.bind("<Escape>", lambda e: self.root.destroy())
		self.root.geometry(f"{self.boardSize*2}x{self.boardSize*2}")
		self.root.bind("B", lambda x: breakpoint())

		# Paned Window
		self.pWindow = ttk.PanedWindow(self.root, orient="horizontal")
		self.pWindow.pack(fill="both", expand=1)

		# Frame container for board canvas
		self.boardFrame = tk.Frame(self.pWindow, bg="gray75")
		self.boardFrame.bind("<Configure>", self.resizeBoard)

		# Board Canvas
		self.canvas = sqCanvas(self.boardFrame)
		self.canvas.bind('<Button>', self.humanMove)
		self.canvas.pack()

		# Frame for control panel
		self.controlFrame = tk.Frame(self.pWindow, bg="pink")

		# Button Bar Frame
		self.buttonBarFrame = tk.Frame(self.controlFrame, bg="blue")
		self.buttonBarFrame.pack(anchor="n", fill='x', expand=1)

		# Button Bar Label
		self.buttonBarLabel = tk.Label(self.buttonBarFrame, text="Button Bar")
		self.buttonBarLabel.pack()
		
		# Add widgets to paned window
		self.pWindow.add(self.boardFrame, weight=1)
		self.pWindow.add(self.controlFrame, weight=1)


	def createCanvasObjects(self):
		# create 64 rectangles to be sized and positioned later
		flipColor = {
			self.lightColorSq : self.darkColorSq,
			self.darkColorSq : self.lightColorSq
		}
		sqColor = self.lightColorSq
		sqLabel = 1
		for col in range(8):
			for row in range(8):
				sqId = self.canvas.create_rectangle(1, 1, 10, 10, fill=sqColor)
				self.squares.append(sqId)
				if sqColor == self.darkColorSq:
					darkSqLabelId = self.canvas.create_text(
						(1, 1),
						fill="white",
						text= str(sqLabel),
					)
					self.sqLabels.append(darkSqLabelId)
					self.darkSquares.append(sqId)
					sqLabel += 1
				sqColor = flipColor[sqColor]
			sqColor = flipColor[sqColor]


	def makeMove(self):
		while self.isRunning == True:
			self.board.getLegalMoves()
			if len(self.board.legalMoves) == 0: break
			player = self.bp if self.board.onMove == 1 else self.wp
			if type(player) == str:
				return
			move = player.selectMove()
			if move in self.board.legalMoves2FEN():
				self.board.makeMove(move)
				self.updateGUI(move)


	def humanMove(self, pos):
		'''
		Let humans make a move with mouse click on the board
		'''
		fenSqNo = self.getFENSqNo(pos)
		if fenSqNo == None: return
		if self.MiP == None:
			MiP = self.board.legalMoves2FEN()
			idx = 0
		else:
			MiP = self.MiP['moves']
			idx = self.MiP['depth']
		moveMatches = list(filter(lambda x: x[idx] == fenSqNo, MiP))
		
		# if only 1 move is left, make it
		if len(moveMatches) == 1:
			self.board.makeMove(moveMatches[0])
			self.unHighLightSquares()
			self.MiP = None
			self.updateGUI(moveMatches[0])
			self.makeMove()
		# if move does not make sense, start over
		elif len(moveMatches) == 0:
			self.unHighLightSquares()
			self.MiP = None
		else:
			self.MiP = {
				"depth" : idx+1,
				"moves" : moveMatches
			}
			# light up legal next move squares
			landing = []
			for sq in self.MiP['moves']:
				if sq[idx+1] not in landing:
					landing.append(sq[idx+1])
			self.unHighLightSquares()
			self.highlightSquares(landing)


	def updateGUI(self, move):
		'''
		Update the men and kings on the board to reflect a move
		@param move: list: list of ints representing the FEN square numbers or a move
		'''
		self.pieceAnimate(move)
		# remove jumped pieces
		if abs(move[0] - move[1]) > 5:
			for i, sq in enumerate(move):
				# the starting piece has been moved to landing square already
				if i == 0: continue
				jumpSq = (sq + move[i-1])//2 if sq in GUI.ODD_ROW_SQUARES else (sq + move[i-1]+1)//2
				self.canvas.delete(self.returnPiece(jumpSq))
		# promote to king
		end = move[-1]
		if end in (1,2,3,4,29,30,31,32):
			piece = self.returnPiece(end)
			self.canvas.itemconfigure(piece, outline="white", width=2)


	def pieceAnimate(self, move):
		'''
		Move piece from starting square to landing square in increments
		@param move: list: list of ints representing a move
		'''
		startCoords = self.canvas.coords(self.darkSquares[move[0] - 1])
		endCoords = self.canvas.coords(self.darkSquares[move[-1] - 1])
		difX = endCoords[0]-startCoords[0]
		difY = endCoords[1]-startCoords[1]
		pieceId = self.returnPiece(move[0])
		counter = 0
		inc = 15
		while counter < inc:
			self.canvas.move(pieceId, difX/inc, difY/inc)
			counter += 1
			self.root.update()
		time.sleep(.02)


	def returnPiece(self, sqNo):
		'''
		Return the canvas id number of the man on sqNo
		@param sqNo: int: FEN square number where you want to find the piece
		'''
		sqCoor = self.canvas.coords(self.darkSquares[sqNo-1])
		sqItems = self.canvas.find_enclosed(
			sqCoor[0],
			sqCoor[1],
			sqCoor[0]+(self.boardSize/8),
			sqCoor[1]+(self.boardSize/8)
		)
		# return the top level object id
		return sqItems[-1]


	def highlightSquares(self, FENSqNoList):
		'''
		Highlight the clicked dark square
		@ param FENSqNo: list: The FEN square numbers of squares to highlight
		'''
		for sq in FENSqNoList:
			darkSqId = self.darkSquares[sq-1]
			self.canvas.itemconfigure(darkSqId, fill=self.litSqColor)
			self.canvas.addtag_withtag("litSq", darkSqId)


	def unHighLightSquares(self):
		'''
		Return all highlighted dark squares to original color
		'''
		self.canvas.itemconfigure("litSq", fill=self.darkColorSq)
		self.canvas.dtag("litSq", "litSq")


	def getFENSqNo(self, pos):
		'''
		Return FEN square number from mouse click position
		@ param pos: tkinter.Event: providing the x,y coordinate of mouse click
		@ return int: FEN Square number. Light color square are ignored
		'''
		sqSize = self.boardSize/8
		squareLoc = ( pos.y // sqSize, pos.x // sqSize )
		# react only to dark square clicks
		if squareLoc[0] % 2 == squareLoc[1] % 2: return None
		return int((squareLoc[0] * 4) + 1 + (squareLoc[1]/2))


	def positionCanvasObjects(self):
		'''
		re-position squares and labels based on current value 
		of self.boardSize
		'''
		# get current board FEN position
		xpos, ypos, sqIds, lblIds = 0, 0, 0, 0
		sqSize = self.boardSize/8
		for col in range(8):
			for row in range(8):
				self.canvas.coords(self.squares[sqIds], xpos, ypos, xpos+sqSize, ypos+sqSize)
				# if dark square, move its label too
				if ((row+col)%2==1):
					self.canvas.coords(self.sqLabels[lblIds], (xpos+8, ypos+8))
					lblIds+=1
				xpos += sqSize
				sqIds+=1
			ypos += sqSize
			xpos = 0


	def drawPieces(self):
		'''
		Draw men and kings on board
		'''
		self.canvas.delete('pieces')
		offset = 7
		fenPos = self.board.pos2Fen()
		for i, sqIdx in enumerate(self.board.FEN2Pos):
			sq = self.board.position[sqIdx]
			if sq <= 0: continue
			color = 'black' if sq <= 2 else 'red'
			kingSign = 2 if sq%2 == 0 else 0
			sqCoords = self.canvas.coords(self.darkSquares[i])
			self.canvas.create_oval(
				sqCoords[0]+offset,
				sqCoords[1]+offset,
				sqCoords[2]-offset,
				sqCoords[3]-offset,
				fill = color,
				outline = 'white',
				width = kingSign,
				tags = "pieces"
			)


	def resizeBoard(self, e):
		''' 
		redraw board and men based on width of container.
		bound to change in board frame container size
		'''
		self.boardSize = min(e.height, e.width)
		self.positionCanvasObjects()
		self.drawPieces()
		
if __name__ == '__main__':
	rt = '[FEN "W:W27,19,18,11,7,6,5:B28,26,25,20,17,10,9,4,3,2"]'
	jumpers = '[FEN "B:W18,26,27,25,11,19:BK15,K14"]'
	b = board2.Board(rt)
	e = engines.littlebitB(b, maxdepth=13, randomize=False, ab=True)
	GUI(b, wp=e)