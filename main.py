import pygame as pg
import random, math
from gridBoard import *
from mathinnate import *
import mathiShapes as sh

pg.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1200
GRID_WIDTH = 10
GRID_HEIGHT = 10

## TODO
# - panning and zooming around (screensaver) @Qwertious :D
# - Regen Animation = rain animation
# - Schatten von Bergen = shadow of the mountains (so its a 3D effect)
# - Tiere (animals)
#
## DONE
# - GRID_WIDTH und GRID_HEIGHT wenn unterschiedlich skalierung und pos fix DONE
#

window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pg.time.Clock()

ColorPalate = {
    GridTypes.Ground: pg.Color(99, 62, 32),
    GridTypes.Plant: pg.Color(0, 181, 12),
    GridTypes.Animal: pg.Color(255, 0, 0)
}

def mutateColor(color: pg.Color):
    newR = min(max(color.r + random.randint(-6, 6), 0), 255)
    newG = min(max(color.g + random.randint(-6, 6), 0), 255)
    newB = max(min(color.b + random.randint(-6, 6), 255), 0)
    rRange = (10, 120)
    gRange = (30, 200)
    bRange = (10, 60)
    color.r = min(max(newR, rRange[0]), rRange[1])
    color.g = min(max(newG, gRange[0]), gRange[1])
    color.b = min(max(newB, bRange[0]), bRange[1])

class Data:
    def __init__(s):
        s.board: GridBoard = GridBoard(GRID_WIDTH, GRID_HEIGHT)
        s.boardOld: GridBoard = GridBoard(GRID_WIDTH, GRID_HEIGHT)
        s.outLineRects: list[sh.Rect] = []
        s.innerRects: list[sh.Rect] = []
        s.mountainShadows: list[sh.Polygon] = []
        s.simulationTimer: int = 0
        s.board.populate()
        s.framePercent: float = 0
        s.SimTickTime = 1000
        s.NewSimTickTime = 1000

        s.cellWidth = WINDOW_WIDTH / GRID_WIDTH
        s.cellHeight = WINDOW_HEIGHT / GRID_HEIGHT
        s.cellMarginX = s.cellWidth / 6
        s.cellMarginY = s.cellHeight / 6

        s.rainingChance = 0.1
        s.rainingStrength = 40

def simulationTick(data : Data):# 1/s
    grid : GridBoard = data.board
    gridNew : GridBoard = data.board.copy()

    if random.random() < data.rainingChance:
        startPos = (
            random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        facing = math.radians(random.randint(0, 359))
        cloudLength = data.rainingStrength * (random.random() / 4 + 0.75)
        cloudLength = round(cloudLength)

        rainingPositions: list[tuple[int, int]] = []
        currentPos = startPos
        for i in range(cloudLength):
            x, y = round(currentPos[0]), round(currentPos[1])
            if (x, y) not in rainingPositions and random.random() < 0.9:
                rainingPositions.append((x, y))

            facingVector = (math.cos(facing), math.sin(facing))
            facing += (random.random() - 0.5) / 3

            currentPos = addPos(currentPos, facingVector)

        neighbrous = []
        for pos in rainingPositions:
            for newPos in gridNew.adjacent(pos):
                if newPos not in rainingPositions:
                    neighbrous.append(newPos)
        
        for n in neighbrous:
            if random.random() < 0.7:
                rainingPositions.append(n)
            for newPos in gridNew.adjacent(n):
                if (newPos not in rainingPositions
                   and newPos not in neighbrous
                   and random.random() < 0.5):
                    rainingPositions.append(newPos)

        RA = random.random() / 5
        RT = random.randint(5,40)
        for position in rainingPositions:
            state: GridState = gridNew.Get(gridNew.wrap(position))
            state.rainAmount = RA
            state.rainTime = RT

    for pos in grid:
        grid.Get(pos).waterPreTick()

    for pos in grid:
        
        grid.Get(pos).tick(gridNew.Get(pos))
        #gridNew.Get(pos).removePlant()
        stateNew = gridNew.Get(pos)
        state = grid.Get(pos)
        possibleOld = []
        grassNabu = False
        for posi in grid.adjacent(pos):
            if grid.Get(posi).canPlantMakeSapling(gridNew.Get(posi), state):
                grassNabu = True
                possibleOld.append(posi)

        if grassNabu:
            parent = random.choice(possibleOld)
            stateParentNew = gridNew.Get(parent)
            stateParent    = grid.Get(parent)
            if state.canPlantGrow(stateParent.color):
                stateParent.plantMakeSapling(stateParentNew)
                stateNew.setPlant(pg.Color(stateParent.color), parent)
                mutateColor(stateNew.color)

        else:
            stateNew.parent = pos
            
    
    data.board = gridNew
    data.boardOld = grid

    #for pos in data.board:
    #    data.board.setVal(pos, random.randint(0,2))

def tickLogic(data: Data):# 180/s0
    if data.simulationTimer >= data.SimTickTime:
        data.simulationTimer -= data.SimTickTime
        simulationTick(data)
        data.SimTickTime = data.NewSimTickTime
    data.framePercent = (data.simulationTimer % data.SimTickTime) / data.SimTickTime

def drawSetup(D: Data):
    grid: GridBoard = D.board
    
    for x, y in grid:
        outer = sh.Rect(x * D.cellWidth, y * D.cellHeight,
                        D.cellWidth + 1, D.cellHeight + 1)
        D.outLineRects.append(outer)

        shadowRect = outer.copy()
        shadowRect.x += 50
        shadowRect.y += 50
        shadow = sh.Polygon(outer, shadowRect)
        D.mountainShadows.append(shadow)

        inner = sh.Rect(x * D.cellWidth + D.cellMarginX,
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
        waterColor = pg.Color(53, 134, 222)
        water = grid.Get(x,y).waterPercent
        waterOld = gridOld.Get(x,y).waterPercent
        water = lerp(waterOld, water, lerpVal)
        D.outLineRects[x + y * grid.Width].draw(window, newColor.lerp(waterColor, max(min(water, 1), 0)), 0)

        
    for x, y in grid:
        inner : sh.Rect = D.innerRects[x + y * grid.Width]
        state : GridState = grid.Get(x, y)
        oldState : GridState = gridOld.Get(x, y)

        if (state.type == GridTypes.Plant and
            oldState.type == GridTypes.Ground):
            posLerp = easeOutCubic(lerpVal * 2)
            sizeLerp = easeInOutSine(lerpVal * 2 - 1)
            
            smallpercent = 0.5

            if manhattanDistance(state.parent, (x,y)) <= 2:
                nX, nY = lerpPos(state.parent, (x,y), posLerp)
                inner.rotation = lerp(0, math.radians(180), posLerp)
            else:
                richtung = (((x + 1) % grid.Width ) - ((state.parent[0] + 1) % grid.Width ),
                            ((y + 1) % grid.Height) - ((state.parent[1] + 1) % grid.Height))
                if posLerp < 0.5:
                    nX, nY = lerpPos(state.parent, addPos(state.parent, richtung), posLerp)
                else:
                    nX, nY = lerpPos(subPos((x,y), richtung), (x, y), posLerp)

            width = D.cellWidth - 2 * D.cellMarginX
            height = D.cellHeight - 2 * D.cellMarginY
            nX, nY = (nX * D.cellWidth + D.cellMarginX, nY * D.cellHeight + D.cellMarginY)

            inner.x, inner.y = lerpPos((nX + width * (1 - smallpercent) / 2,
                            nY + height * (1 - smallpercent) / 2), (nX, nY), sizeLerp)

            
            inner.width = lerp(width * smallpercent, width, sizeLerp)
            inner.height = lerp(height * smallpercent, height, sizeLerp)

            borderRadius = D.cellMarginX / 2
            borderRadius = lerp(borderRadius * smallpercent, borderRadius, sizeLerp)
            inner.draw(window, state.color, int(borderRadius))
                
        # Plant dies
        elif (state.type == GridTypes.Ground and
            oldState.type == GridTypes.Plant):
            sizeLerp = easeInOutSine(lerpVal)

            smallpercent = 0
            nX, nY = (x * D.cellWidth + D.cellMarginX, y * D.cellHeight + D.cellMarginY)
            width = D.cellWidth - 2 * D.cellMarginX
            height = D.cellHeight - 2 * D.cellMarginY
            inner.x, inner.y = lerpPos((nX, nY), (nX + width * (1 - smallpercent) / 2,
                            nY + height * (1 - smallpercent) / 2), sizeLerp)
            
            inner.width = lerp(width, width * smallpercent, sizeLerp)
            inner.height = lerp(height, height * smallpercent, sizeLerp)
            borderRadius = D.cellMarginX / 2
            borderRadius = lerp(borderRadius, borderRadius * smallpercent, sizeLerp)
            inner.rotation = lerp(0, math.pi * 2, sizeLerp)
            inner.draw(window, state.color, int(borderRadius))
            
            
        elif state.type != GridTypes.Ground:
            inner.draw(window, state.color, int(D.cellMarginX / 2))

    shadowColor = pg.Color(30, 30, 30, 50)
    D.mountainShadows[13].draw(window, shadowColor)



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
                
        keys = pg.key.get_pressed()
        
        if keys[pg.K_UP]:
            data.NewSimTickTime /= 2
        if keys[pg.K_DOWN]:
            data.NewSimTickTime *= 2

        window.fill('black')

        tickLogic(data)
        tickDraw(window, data)
        pg.display.flip()

        pg.transform.rotate(window, 10)
        clock.tick(180)
        data.simulationTimer += clock.get_time()

if __name__ == "__main__":
    mainLoop()
