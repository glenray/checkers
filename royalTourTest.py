import engines
from board2 import Board

royalTour = [
    '[FEN "W:W27,19,18,11,7,6,5:B28,26,25,20,17,10,9,4,3,2"]',
    '[FEN "B:W27,18,15,11,5,6,7:B25,26,28,17,20,9,10,2,3,4"]',
    '[FEN "W:W27,18,11,5,6,7:B25,26,28,17,19,20,9,2,3,4"]',
    '[FEN "B:W27,18,11,6,7,K1:B25,26,28,17,19,20,9,2,3,4"]',
    '[FEN "W:W27,18,11,6,K1:B25,26,28,17,19,20,9,10,2,4"]',
    '[FEN "B:W27,18,6,8,K1:B25,26,28,17,19,20,9,10,2,4"]',
    '[FEN "W:W27,18,6,K1:B25,26,28,17,19,20,9,10,11,2"]',
    '[FEN "B:W24,18,6,K1:B25,26,28,17,19,20,9,10,11,2"]',
    '[FEN "W:W18,6,K1:B25,26,27,28,17,19,9,10,11,2"]',
    '[FEN "B:W14,6,K1:B25,26,27,28,17,19,9,10,11,2"]',
    '[FEN "W:W6,K1:B25,26,27,28,17,18,19,10,11,2"]',
    '[FEN "B:WK5,6:B25,26,27,28,17,18,19,10,11,2"]',
    '[FEN "W:WK5:B25,26,27,28,17,18,19,9,10,11"]',
    '[FEN "B:WK32:B28"]'
]
royalTour.reverse()

def run(EngineClass, kwargs = None):
    maxdepth = 1
    for position in royalTour:
        b = Board(position)
        engine = EngineClass(b, maxdepth=maxdepth, **kwargs)
        move = engine.selectMove()
        print(f'{engine.name} as {"White" if b.onMove == -1 else "Black"} moves {move}\n\tScore: {engine.score}, Nodes: {engine.totalNodes}, NPS: {engine.nps}, Time: {engine.elapsedTime}')
        if engine.elapsedTime > 5*60:
            print("TimeOut")
            return
        maxdepth+=1
    print("Congratulations. You have solved the Royal Tour Problem!")

if __name__ == '__main__':
    e = engines.negamax
    params = {'ab' : True, 'randomize' : False}
    run(e, params)