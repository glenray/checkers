class moveNode:
	def __init__(self, board, parent = None):
		self.board = board
		self.parent = parent
		self.children = []

	def addChild(self, child):
		self.children.append(child)
		child.parent = self

	def printChildren(self):
		for i, child in enumerate(self.children):
			print(i)
			print(child.__repr__())

	def getRootNode(self):
		''' Returns tree root node '''
		if self.parent == None:
			return self
		x = self.parent
		while True:
			if x.parent == None:
				return x
			else:
				x = x.parent

	def printSiblings(self):
		if self.parent:
			for child in self.parent.children:
				print(child)

	def countNodes(self):
		''' Return count of this nodes children and all decendents '''
		return self._countChildren() + len(self.children)

	def _countChildren(self):
		''' 
		Return the count of all child nodes under the current node
		This does not include the child nodes within the current node
		'''
		n = 0
		for child in self.children:
			n+=len(child.children)
			n+=child._countChildren()
		return n

	def getLeafNodes(self):
		'''
		@return: list: list of nodes from bottom of tree, i.e.,
			those no children
		'''
		result = []
		for child in self.children:
			if child.children:
				result += child.getLeafNodes()
			else:
				result.append(child)
		return result


	def __repr__(self):
		return self.board.printBoard()


class littleBNode:
	def __init__(self, reperMethod, position, parent = None):
		self.reperMethod = reperMethod
		self.parent = parent
		self.children = []
		self.position = position

	def addChild(self, child):
		self.children.append(child)
		child.parent = self

	def printChildren(self):
		for i, child in enumerate(self.children):
			print(i)
			print(child.__repr__())

	def getRootNode(self):
		''' Returns tree root node '''
		if self.parent == None:
			return self
		x = self.parent
		while True:
			if x.parent == None:
				return x
			else:
				x = x.parent

	def printSiblings(self):
		if self.parent:
			for child in self.parent.children:
				print(child)

	def countNodes(self):
		''' Return count of this nodes children and all decendents '''
		return self._countChildren() + len(self.children)

	def _countChildren(self):
		''' 
		Return the count of all child nodes under the current node
		This does not include the child nodes within the current node
		'''
		n = 0
		for child in self.children:
			n+=len(child.children)
			n+=child._countChildren()
		return n

	def getLeafNodes(self):
		'''
		@return: list: list of nodes from bottom of tree, i.e.,
			those no children
		'''
		result = []
		for child in self.children:
			if child.children:
				result += child.getLeafNodes()
			else:
				result.append(child)
		return result


	def __repr__(self):
		return self.reperMethod(self.position[1])
