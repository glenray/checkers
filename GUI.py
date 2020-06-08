import tkinter as tk
import tkinter.ttk as ttk
from sqCanvas import sqCanvas

class GUI:
	def __init__(self):
		self.boardSize = 300
		self.lightColorSq = "yellow"
		self.darkColorSq = "blue"
		self.squares = []		# list of ids for canvas rectangles
		self.sqLabels = []		# list of ids for dark square number labels

		self.createWidgets()
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
		self.canvas.pack()

		# Frame for control panel
		self.controlFrame = tk.Frame(self.pWindow, bg="pink")
		
		# Add widgets to paned window
		self.pWindow.add(self.boardFrame, weight=1)
		self.pWindow.add(self.controlFrame, weight=1)

		self.createRectangles()
		self.positionSquares()

	# re-position squares based on current value of self.boardSize
	def positionSquares(self):
		xpos, ypos, sqIds, lblIds = 0, 0, 0, 0
		sqSize = self.boardSize/8
		for row in range(8):
			for col in range(8):
				self.canvas.coords(self.squares[sqIds], xpos, ypos, xpos+sqSize, ypos+sqSize)
				# if dark square, move its label too
				if ((row+col)%2==1):
					self.canvas.coords(self.sqLabels[lblIds], (xpos+8, ypos+8))
					lblIds+=1
				xpos += sqSize
				sqIds+=1
			ypos += sqSize
			xpos = 0

	# create 64 rectangles to be sized and positioned later
	def createRectangles(self):
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
						text= str(sqLabel)
						)
					self.sqLabels.append(darkSqLabelId)
					sqLabel += 1
				sqColor = flipColor[sqColor]
			sqColor = flipColor[sqColor]

	''' Event bindings '''
	# bound to change in board frame container size, redraw board based on width of container
	def resizeBoard(self, e):
		self.boardSize = min(e.height, e.width)
		self.positionSquares()
		

if __name__ == '__main__':
	GUI()