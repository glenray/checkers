import pkgutil
import importlib
import board


'''
iterate the engine package and store each module in an array
'''
names = [name for _, name, _ in pkgutil.iter_modules(['engines'])]
b = board.Board()

engines = {}
for engine in names:
	# engines[engine] = importlib.import_module("engines."+engine)
	a = importlib.import_module("engines."+engine)
	print(a.player(b))

