import pygame as pg
import random, math
from gridBoard import *
from mathinnate import *

pg.init()

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 1400
GRID_WIDTH = 10
GRID_HEIGHT = 10

window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pg.time.Clock()

ColorPalate = {
    GridTypes.Ground: pg.Color(99, 62, 32),
    GridTypes.Plant: pg.Color(0, 181, 12),
    GridTypes.Animal: pg.Color(255, 0, 0)
}

def mutateColor(color: pg.Color):
    color.r = min(max(color.r + random.randint(-10, 10), 0), 255)
    color.g = min(max(color.g + random.randint(-10, 10), 0), 255)
    color.b = max(min(color.b + random.randint(-10, 10), 255), 0)

class Data:
    def __init__(s):
        s.board: GridBoard = GridBoard(GRID_WIDTH,GRID_HEIGHT)
        s.boardOld: GridBoard = GridBoard(GRID_WIDTH,GRID_HEIGHT)
        s.outLineRects: list[pg.Rect] = []
        s.innerRects: list[pg.Rect] = []
        s.simulationTimer: int = 0
        s.board.populate()
        s.framePercent: float = 0
        s.SimTickTime = 1000
        s.GrowPercent = 1

        s.cellWidth = WINDOW_WIDTH / GRID_WIDTH
        s.cellHeight = WINDOW_HEIGHT / GRID_HEIGHT
        s.cellMarginX = s.cellWidth / 10
        s.cellMarginY = s.cellHeight / 10

def simulationTick(data : Data):# 1/s
    grid : GridBoard = data.board
    gridNew : GridBoard = data.board.copy()
    
    for pos in grid:
        #= (random.randint(0,grid.Width - 1),
        #random.randint(0,grid.Height - 1))
        grassNabu = False
        possibleOld = []
        state = gridNew.Get(pos)
        stateOld = grid.Get(pos)
        for posi in grid.adjacent(pos):
            if (grid.Get(posi).type == GridTypes.Plant and
                random.random() < data.GrowPercent):
                grassNabu = True
                possibleOld.append(posi)
        if grassNabu and state.canGrow(grid.Get(state.Old).Color):
            state.type = GridTypes.Plant
            state.Old = random.choice(possibleOld)
            state.Color = pg.Color(grid.Get(state.Old).Color) #### VIELLEICHT KOPIEREN WEIL REFERENZ
            mutateColor(state.Color)
        else:
            state.Old = pos
        stateOld.tick(state, data)
            
    data.board = gridNew
    data.boardOld = grid
    #for pos in data.board:
    #    data.board.setVal(pos, random.randint(0,2))

def tickLogic(data: Data):# 180/s0
    while data.simulationTimer >= data.SimTickTime:
        data.simulationTimer -= data.SimTickTime
        simulationTick(data)
    data.framePercent = (data.simulationTimer % data.SimTickTime) / data.SimTickTime

def drawSetup(D: Data):
    grid: GridBoard = D.board
    
    for x, y in grid:
        outer = pg.Rect(x * D.cellWidth, y * D.cellHeight,
                        D.cellWidth + 1, D.cellHeight + 1)
        D.outLineRects.append(outer)

        inner = pg.Rect(x * D.cellWidth + D.cellMarginX,
                        y * D.cellHeight + D.cellMarginY,
                        D.cellWidth - 2 * D.cellMarginX,
                        D.cellHeight - 2 * D.cellMarginY)
        D.innerRects.append(inner)


def tickDraw(window: pg.Surface, D: Data):# 180/s
    grid: GridBoard = D.board
    gridOld: GridBoard = D.boardOld
    lerpVal = D.framePercent
    
    for x, y in grid:
        newColor = pg.Color(ColorPalate[0])
        waterColor = pg.Color(0, 0, 150)
        water = grid.Get(x,y).WaterPercent
        waterOld = gridOld.Get(x,y).WaterPercent
        water = lerp(waterOld, water, lerpVal)
        pg.draw.rect(window, newColor.lerp(waterColor, water), D.outLineRects[x + y * grid.Width])
        
    for x, y in grid:
        inner : pg.Rect = D.innerRects[x + y * grid.Width]
        state : GridState = grid.Get(x, y)
        oldState : GridState = gridOld.Get(x, y)

        if (state.type == GridTypes.Plant and
            oldState.type == GridTypes.Ground):
            posLerp = easeOutCubic(lerpVal * 2)
            sizeLerp = easeInOutSine(lerpVal * 2 - 1)
            
            smallpercent = 0.5

            if manhattanDistance(state.Old, (x,y)) <= 1:
                nX, nY = lerpPos(state.Old, (x,y), posLerp)
            else:
                richtung = (((x + 1) % grid.Width ) - ((state.Old[0] + 1) % grid.Width ),
                            ((y + 1) % grid.Height) - ((state.Old[1] + 1) % grid.Height))
                if posLerp < 0.5:
                    nX, nY = lerpPos(state.Old, addPos(state.Old, richtung), posLerp)
                else:
                    nX, nY = lerpPos(subPos((x,y), richtung), (x, y), posLerp)

            nX, nY = (nX * D.cellWidth + D.cellMarginX, nY * D.cellHeight + D.cellMarginY)
            inner.top, inner.left = lerpPos((nX + D.cellWidth * (1 - smallpercent) / 2,
                            nY + D.cellHeight * (1 - smallpercent) / 2), (nX, nY), sizeLerp)
            width = D.cellWidth - 2 * D.cellMarginX
            height = D.cellHeight - 2 * D.cellMarginY

            
            inner.width = lerp(width - D.cellWidth * (1 - smallpercent), width, sizeLerp)
            inner.height = lerp(height - D.cellHeight * (1 - smallpercent), height, sizeLerp)
            pg.draw.rect(window, state.Color, inner,
                        0, int((D.cellMarginX + D.cellHeight) / 15))
                
        # Plant dies
        elif (state.type == GridTypes.Ground and
            oldState.type == GridTypes.Plant):
            sizeLerp = easeInOutSine(lerpVal)

            smallpercent = 0.2
            nX, nY = (x * D.cellWidth + D.cellMarginX, y * D.cellHeight + D.cellMarginY)
            inner.top, inner.left = lerpPos((nX, nY), (nX + D.cellWidth * (1 - smallpercent) / 2,
                            nY + D.cellHeight * (1 - smallpercent) / 2), sizeLerp)
            width = D.cellWidth - 2 * D.cellMarginX
            height = D.cellHeight - 2 * D.cellMarginY
            
            inner.width = lerp(width, width - D.cellWidth * (1 - smallpercent), sizeLerp)
            inner.height = lerp(height, height - D.cellHeight * (1 - smallpercent), sizeLerp)
            pg.draw.rect(window, state.Color, inner,
                        0, int((D.cellMarginX + D.cellHeight) / 15))
            
        elif state.type != GridTypes.Ground:
            pg.draw.rect(window, state.Color, inner,
                        0, int((D.cellMarginX + D.cellHeight) / 15))



def mainLoop():
    running = True
    data = Data()
    drawSetup(data)
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                running = False

        window.fill('black')

        tickLogic(data)
        tickDraw(window, data)
        pg.display.flip()

        pg.transform.rotate(window, 10)
        clock.tick(180)
        data.simulationTimer += clock.get_time()

if __name__ == "__main__":
    mainLoop()
