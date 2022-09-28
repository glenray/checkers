import tkinter as tk
import tkinter.ttk as ttk
import time
import board2
from sqCanvas import sqCanvas

class GUI:
	def __init__(self, board=None):
		'''
		@param board: board2.Board object
		'''
		self.board = board
		self.boardSize = 400
		self.lightColorSq = "yellow"
		self.darkColorSq = "blue"
		self.litSqColor = "green"
		self.squares = []		# list of ids for canvas rectangles
		self.darkSquares = []	# list of ids for dark squares
		self.sqLabels = []		# list of ids for dark square number labels
		self.MiP = None			# for human moves in progress

		self.createWidgets()
		self.createCanvasObjects()
		self.positionCanvasObjects()
		self.drawPieces()		
		self.root.mainloop()


	def createWidgets(self):
		# The window
		self.root = tk.Tk()
		self.root.title("Glen's Checkers")
		self.root.bind("<Escape>", lambda e: self.root.destroy())
		self.root.geometry(f"{self.boardSize*2}x{self.boardSize*2}")

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
		pass

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
		self.pieceAnimate(move)
	

	def returnPiece(self, coord):
		pass


	def pieceAnimate(self, move):
		startSqId = move[0] - 1
		endSqId = move[-1] - 1
		startCoords = self.canvas.coords(self.darkSquares[startSqId])
		endCoords = self.canvas.coords(self.darkSquares[endSqId])
		difY = startCoords[1]-endCoords[1]
		difX = startCoords[0]-endCoords[0]
		sqItems = self.canvas.find_enclosed(
			startCoords[0],
			startCoords[1],
			startCoords[0]+(self.boardSize/8),
			startCoords[1]+(self.boardSize/8)
		)
		pieceId = sqItems[-1]


		# move piece from starting square to landing square in increments
		counter = 0
		inc = 15
		while counter < inc:
			self.canvas.move(pieceId, difY/inc, difX/inc)
			counter += 1
			self.root.update()
			time.sleep(.02)




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
	b = board2.Board('[FEN "B:W18,26,27,25,11,19:BK15,K14"]')
	GUI(b)