import pygame as pg
import random

pg.init()

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 1400
window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pg.time.Clock()

class GridStates:
    Ground = 0
    Plant = 1
    Animal = 2
    AnimalOnPlant = 3

ColorPalate = {
    GridStates.Ground: (0, 0, 0)
    ,GridStates.Plant:(0, 255, 0)
    ,GridStates.Animal:(255, 0, 0)}
    
class GridBoard:
    nab= [(0,1),(0,-1),(1,0),(-1,0)]
    def __init__(s, width, height):
        s.board = []
        row = []
        s.Width = width
        s.Height = height
        for _ in range(height):
            row.append(GridStates.Ground)
        for _ in range(width):
            s.board.append(row.copy())
    def populate(s):
        for pos in s:
            if (random.random() < 0.02):
                s.setVal(pos, GridStates.Plant)
    def contained(s, pos):
        return (0 < pos[0]) and (pos[0] < s.Width) and (0 < pos[1]) and (pos[1] < s.Height)
    def nabu(s, pos):
        for a in GridBoard.nab:
            newPos = (pos[0]+a[0], pos[1]+a[1])
            if s.contained(newPos): yield newPos
    def getVal(s, pos):
        return s.board[pos[0]][pos[1]]
    def setVal(s, pos, Value):
        s.board[pos[0]][pos[1]] = Value
    def __iter__(s):
        for a in range(s.Width):
            for b in range(s.Height):
                yield (a,b)

class Data:
    def __init__(s):
        s.board : GridBoard = GridBoard(10,10)
        s.board2 : GridBoard = GridBoard(10,10)
        s.simulationTimer : int = 0
        s.board.populate()

def simulationTick(data):# 1/s
    grid : GridBoard = data.board
    pos = (random.randint(0,grid.Width - 1),
    random.randint(0,grid.Height - 1))
    grassNabu = False
    for posi in grid.nabu(pos):
        if grid.getVal(posi) == GridStates.Plant:
            grassNabu = True
    if grassNabu: grid.setVal(pos, GridStates.Plant)
    #for pos in data.board:
    #    data.board.setVal(pos, random.randint(0,2))

def tickLogic(data: Data):# 180/s
    if data.simulationTimer >= 100:
        data.simulationTimer -= 100
        simulationTick(data)

def tickDraw(window: pg.Surface, data):# 180/s
    grid : GridBoard = data.board
    
    cellWidth = WINDOW_WIDTH / grid.Width
    cellHeight = WINDOW_HEIGHT / grid.Height
    cellMarginX = cellWidth / 30
    cellMarginY = cellHeight / 30
    
    for x, y in grid:
        outer = pg.Rect(x * cellWidth, y * cellHeight, cellWidth, cellHeight)
        inner = pg.Rect(x * cellWidth + cellMarginX, y * cellHeight + cellMarginY,
                        cellWidth - 2 * cellMarginX, cellHeight - 2 * cellMarginY)
            
        
        pg.draw.rect(window, (0, 0, 0), outer)
        pg.draw.rect(window, ColorPalate[grid.getVal((x, y))], inner,
                      0, int((cellMarginX + cellHeight) / 10))



def mainLoop():
    running = True
    data = Data()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        window.fill('black')

        tickLogic(data)
        tickDraw(window, data)
        pg.display.flip()

        clock.tick(180)
        data.simulationTimer += clock.get_time()

if __name__ == "__main__":
    mainLoop()
