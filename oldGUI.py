'''
To Do:
1. Create resizeable squares and pieces based on change in windows size
2. Modify GUI.py to interface with board2 class with better board representation
'''

from tkinter import *
from tkinter import messagebox
import tkinter as tk
import tkinter.ttk as ttk
import time

# Let's use board2 instead of board
# import board
import board2 as board
from engines import moron
from engines import snap

'''
GUI for checkers
Glen Pritchard 6/17/2018
'''
class GUI:
	def __init__(self, board):
		self.board = board
		self.bPlayer = moron(self.board)
		self.wPlayer = moron(self.board)
		self.lightSqColor = "yellow"
		self.darkSqColor = "blue"
		self.litSqColor = "gray75"
		self.redPieces = "red"
		self.blackPieces = "black"
		self.sqSize = 95
		self.isRunning = True
		self.MiP = None
		
		self.onInit()

	def onInit(self):
		self.windowSetup()
		self.drawBoard()
		self.drawPieces()
		self.canvas.pack(side=LEFT)
		self.textFrame.pack()
		self.bindEvents()
		self.showSettingWindow()
		self.window.mainloop()

	def windowSetup(self):
		self.addWindow()
		self.addScrollBar()
		self.addMoveListFrame()
		self.addCanvas()
		self.addMenuBar()

	def addWindow(self):
		# define the window
		self.window = Tk()
		self.window.geometry(
			"%dx%d%+d%+d" % (self.sqSize*8+300, self.sqSize*8, 20, 20))
		self.window.title("Glen's Checkers")

	def addScrollBar(self):
		# move list scroll bar
		self.scrollBar = Scrollbar(self.window)
		self.scrollBar.pack(side=RIGHT, fill=Y)

	def addMoveListFrame(self):
		# move list
		self.textFrame = Text(
			self.window,
			height = self.sqSize*8,
			width = 30,
			yscrollcommand = self.scrollBar.set,
			state = "disabled"
		)

	def addCanvas(self):
		# board canvas
		self.canvas = Canvas(
			self.window,
			width = self.sqSize*8,
			height = self.sqSize*8,
		)

	def showSettingWindow(self):
		def engChange(e):
			print(players)
			# self.bPlayer = blkCombo.get()(self.board)

		import pkgutil
		#  get list of engine names and prepend human as another option
		players = [name for _, name, _ in pkgutil.iter_modules(['engines'])]
		players.insert(0, 'Human')
		s = Toplevel()
		s.geometry("%dx%d%+d%+d" % (300, 300, 50, 50))
		s.title("Game Settings")
		s.bind('<Escape>', lambda e: close())
		s.attributes("-topmost", True)
		s.rowconfigure(0, pad=20)
		s.columnconfigure(0, pad=20)

		# elements
		blkCombo = ttk.Combobox(s, values=players, state="readonly")
		blkCombo.bind('<<ComboboxSelected>>', engChange)
		blkCombo.current(0)

		whtCombo = ttk.Combobox(s, values=players, state="readonly")
		whtCombo.bind('<<ComboboxSelected>>', engChange)
		whtCombo.current(0)

		goBut = Button(s, text="Go!", command=self.newGame)

		# Layout
		Label(s, text="Black:").grid(row=0)
		blkCombo.grid(row=0, column=1)
		Label(s, text="White:").grid(row=1)
		whtCombo.grid(row=1, column=1)
		goBut.grid(row=2, column=1)

		def close():
			s.destroy()
			self.window.focus_force()
			self.makeMove()

	def addMenuBar(self):
		menubar = Menu(self.window)
		settingMenu = Menu(self.window)
		
		v=tk.IntVar()
		v.set(1)
		# v.trace('w', self.bummer)
		settingMenu.add_radiobutton(label="Option 1", variable=v, value=1, command=lambda:print(v.get()))
		settingMenu.add_radiobutton(label="Option 2", variable=v, value=2, command=lambda:print(v.get()))
		
		menubar.add_command(label="Go", command=self.makeMove)
		menubar.add_command(label="Quit", command=self.window.quit)
		menubar.add_cascade(label="Settings", menu=settingMenu)
		
		self.window.config(menu=menubar)

	# if side on move has 0 legal moves, the game is over
	def __isEOG(self):
		self.board.getLegalMoves()
		if self.board.legalMoves == []:
			whoWon = "Black Wins! " if self.board.onMove == -1 else "Red Wins! "
			# mess = messagebox.showinfo("Game Over", whoWon+"\nGame Over")
			# self.isRunning = False
			# return True
			self.newGame()

	def makeMove(self):
		while self.isRunning == True:
			# check for end of game condition
			if self.__isEOG():
				break			
			# determine which player should move
			player = self.bPlayer if self.board.onMove == 1 else self.wPlayer
			# for humans, wait for input
			# this returns to the onInit method to start main loop
			if player == 'human':
				return
			# ask that player for a move
			breakpoint()
			move, _ = player.selectMove()
			# if the player made a legal move
			if move in self.board.legalMoves:
				self.board.makeMove(move)	# update the board
				self.updateMoveList(move)
				self.updateGUI(move)

	def returnPiece(self, coor):
		piece = self.canvas.find_enclosed(
			coor[1]*self.sqSize,
			coor[0]*self.sqSize,
			coor[1]*self.sqSize+self.sqSize,
			coor[0]*self.sqSize+self.sqSize,
		)
		# does this return the top level object??
		return piece[-1]

	def pieceAnimate(self, move):
		start = move[0]
		end = move[-1]
		piece = self.returnPiece(start)
		difY = (end[1]-start[1])*self.sqSize
		difX = (end[0]-start[0])*self.sqSize

		# move piece from starting square to landing square in increments
		counter = 0
		inc = 15
		while counter < inc:
			self.canvas.move(piece, difY/inc, difX/inc)
			counter += 1
			self.window.update()
			time.sleep(.02)

	def updateGUI(self, move):
		self.pieceAnimate(move)

		# remove jumped pieces
		if abs(move[0][0] - move[1][0]) == 2:
			for i, sq in enumerate(move):
				if i == 0:
					continue
				# the average of the current square and landing square is the jumped piece
				jY = int((sq[0]+move[i-1][0])/2)
				jX = int((sq[1]+move[i-1][1])/2)
				piece = self.returnPiece((jY, jX))
				self.canvas.delete(piece)
 		# king promotion
		end = move[-1]
		if end[0] == 0 or end[0] == 7:
			piece = self.returnPiece(end)
			self.canvas.itemconfigure(piece, outline="white")

	def updateMoveList(self, move):
		output = ""
		append = "\n" if self.board.onMove == 1 else " | "
		for sq in move:
			output += "("+str(sq[0])+" "+str(sq[1])+")"
		output += append
		self.textFrame.configure(state="normal")
		self.textFrame.insert(END, output)
		self.textFrame.configure(state="disabled")

	def drawBoard(self):
		xPos = 0
		yPos = 0
		flipColor = {
			self.lightSqColor : self.darkSqColor, 
			self.darkSqColor : self.lightSqColor}
		sqColor = self.lightSqColor
		sqNum = 1
		for row in range(8):
			for col in range(8):
				self.canvas.create_rectangle(
					xPos, 
					yPos, 
					xPos+self.sqSize, 
					yPos+self.sqSize, 
					fill=sqColor,
				)
				if sqColor == self.darkSqColor:
					self.canvas.create_text(
						(xPos+8, yPos+8),
						fill="white",
						text = str(sqNum)
					)
					sqNum += 1
				sqColor = flipColor[sqColor]
				xPos += self.sqSize
			yPos += self.sqSize
			xPos = 0
			sqColor = flipColor[sqColor]

	def newGame(self):
		self.isRunning = False
		self.board.reset()
		self.canvas.delete('piece')
		self.drawPieces()
		self.isRunning = True
		self.makeMove()

	def bindEvents(self):
		self.canvas.bind('<Button>', self.humanMove)
		self.window.bind('i', self.info)
		self.window.bind('s', lambda e: self.showSettingWindow())
		self.window.bind('<Escape>', lambda e: self.window.destroy())
		self.window.bind('e', lambda e: self.engines())

	def engines(self):
		import pkgutil
		for name in pkgutil.iter_modules(['engines']):
			print(name)

	def info(self, pos):
		for obj in self.canvas.find_all():
			print(
				obj, 
				self.canvas.type(obj),
				self.canvas.gettags(obj),
			)

	# Get human input from screen
	def humanMove(self, pos):
		squareLoc = ( int(pos.y/self.sqSize), int(pos.x/self.sqSize) )
		
		# set move list based on whether this is a new move or coninuation of previous move
		if self.MiP == None:
			self.board.getLegalMoves()
			MiP = self.board.legalMoves
			idx = 0
		else:
			MiP = self.MiP['moves']
			idx = self.MiP['depth']
		# filter move list
		moveMatches = list(filter(lambda x: x[idx] == squareLoc, MiP))
		
		# There is only one move left; make it
		if len(moveMatches)==1:
			self.board.makeMove(moveMatches[0])	# update the board
			self.updateMoveList(moveMatches[0])
			self.updateGUI(moveMatches[0])
			self.MiP = None
			self.unLightSquares()
			self.makeMove()
		# move does not make sense, start over
		elif len(moveMatches)==0:
			self.MiP = None
			self.unLightSquares()
		# more than one move is possible; wait for next touch to narrow it down
		else:
			self.MiP = {
				"depth" : idx+1,
				"moves" : moveMatches
			}
			# light up legal next move squares
			landing = list()
			for sq in self.MiP['moves']:
				if sq[idx+1] not in landing:
					landing.append(sq[idx+1])
			# Highlight possible landing squares
			self.sqLight(landing)

	# highlight landing squares
	def sqLight(self, sqList):
		for sq in sqList:
			obj = self.canvas.find_closest(
				sq[1]*self.sqSize,
				sq[0]*self.sqSize,
			)
			self.canvas.itemconfigure(obj[0], fill=self.litSqColor)
			self.canvas.addtag_withtag("litSq", obj[0])

	def unLightSquares(self):
		self.canvas.itemconfigure("litSq", fill=self.darkSqColor)
		self.canvas.dtag("litSq", "litSq")
	
	def drawPieces(self):
		for Yidx, y in enumerate(self.board.position):
			for Xidx, x in enumerate(y):
				# only bother with dark squares
				if Yidx%2 != Xidx%2:
					if x != 0:
						self.putPiece((Xidx,Yidx))

	def putPiece(self, coordinate):
		pieceValue = self.board.position[coordinate[1]][coordinate[0]]
		# make piece bounding box proportionally smaller than square
		offset = int(self.sqSize*.1)
		x1 = coordinate[0]*self.sqSize
		y1 = coordinate[1]*self.sqSize
		x2 = coordinate[0]*self.sqSize+self.sqSize
		y2 = coordinate[1]*self.sqSize+self.sqSize
		color = self.blackPieces if 1 <= pieceValue <= 2 else self.redPieces
		kingSign = 'white' if pieceValue in (2,4) else ""	#is it a king
		self.canvas.create_oval(
			x1+offset, 
			y1+offset, 
			x2-offset, 
			y2-offset, 
			fill=color, 
			outline = kingSign, 
			width=3, 
			tags="piece"
			)
	
if __name__ == "__main__" :
	positions = {
		"normalStart"	: '[FEN "B:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"]',
		"jump"			: '[FEN "B:W18,19,10:BK15"]',
		"one"			: '[FEN "W:WK21,K25:BK9,10,11,12"]',
		"multiJumpA"	: '[FEN "B:W18,26,27,25,11,19:BK15"]',
		"multiJumpB"	: '[FEN "B:W18,26,27,25,11,19:BK15,K14"]',
		"kingJump"		: '[FEN "B:W17,26,25:B23"]',
		# In this position, snap as white will rock between 32 and 28 indefinitely. Black on move is unable to win or lose, and the game will continue forever. In the same position with white on move, playing randomly, can eventually blunder into a loss.
		"deadDraw"		: '[FEN "B:WK32:BK26"]',
		"royalTour"		: '[FEN "W:W27,19,18,11,7,6,5:B28,26,25,20,17,10,9,4,3,2"]'
	}
	"""
royalTour:
{27-24 Beginning a spectacular shot in which White pitches (almost) all his men
} 1. 19-15 	10x19 2. 5-1 3x10 3. 11-8 4x11 4. 27-24 20x27 5. 18-14 9x18 6. 1-5
2x9 {2-9 and now the coup de grace that inspired the name of this problem...}
7. 5x32 {5-32 (Several different jumping sequences are possible, for example 5
x 14 x 7 x 16 x 23 x 14 x 21 x 30 x 23 x 32) White Wins. As an interesting side
note, this nine-piece jump is the theoretical maximum number of pieces it is
possible to jump in a single turn in checkers (try setting up a 10-piece jump -
the board lacks sufficient space!)} 1-0
"""
	b = board.Board(positions['normalStart'])
	a = GUI(b)