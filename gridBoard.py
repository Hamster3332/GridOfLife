import random
import pygame as pg
import math
from mathinnate import *

class GridTypes:
    Ground = 0
    Plant = 1
    Animal = 2
    AnimalOnPlant = 3

class GridState:
    def __init__(s, pos: tuple[int, int] = (0, 0), Grid = None):
        s.grid : GridBoard = Grid
        s.pos = pos
        #   General
        s.type = GridTypes.Ground
        s.height = 0 #(pos[0] % 10) / 10
        s.rainAmount  = 0
        s.rainTime = 0
        #   Water
        s.waterPercent: float = 0.5
        s.totalFlow: float = 0
        #   Plant
        s.hasPlant = False ## coming soon
        s.plantChange = False ## coming soon
        s.parent: tuple[int, int] = pos
        s.color: pg.Color = pg.Color(99, 62, 32)
        s.plantLife = 0

        s.rainAmount  = 0
        s.rainTime = 0
    
    def copy(s, grid, subTick):
        state = GridState(s.pos, grid)
        #   General
        state.type = s.type
        state.height = s.height
        state.rainAmount = s.rainAmount
        state.rainTime = s.rainTime

        #   Water
        s.waterPercent: float = s.waterPercent
        #s.totalFlow: float = 

        #   Plant
        state.hasPlant = s.hasPlant

        if subTick: state.plantChange = s.plantChange
        else: state.plantChange = False

        state.parent = s.parent
        state.color = s.color
        state.plantLife = s.plantLife
        return state
    
    def setPlant(s, Color : pg.Color, parent : tuple[int, int] = (0, 0)):
        if not s.plantChange and not s.hasPlant:
            s.type = GridTypes.Plant

            s.hasPlant = True
            s.plantChange = True
            s.plantLife = 1
            s.parent = parent
            s.color = Color
            return True
        return False
    
    def removePlant(s):
        if not s.plantChange and s.hasPlant:
            s.type = GridTypes.Ground

            s.hasPlant = False
            s.plantChange = True
            return True
        return False

    def waterPreTick(s):
        s.totalFlow = 0
        for pos in s.grid.adjacent(s.pos):
            adjacentstate = s.grid.Get(pos)
            s.totalFlow += ((s.waterPercent + s.height) -
                    (adjacentstate.waterPercent + adjacentstate.height)) / 4

    def calcWaterScalar(s):
        scalar = 1
        spaceLeft = 1 - s.waterPercent - s.height
        if spaceLeft < 0: print("what")
        if (s.totalFlow <= 0.0001 and s.totalFlow >= - 0.0001 and
            s.waterPercent <= 0.0001):
            s.totalFlow = 0
        elif (s.waterPercent < s.totalFlow):
            scalar = s.waterPercent / s.totalFlow
        elif (spaceLeft < (- s.totalFlow)):
            scalar = spaceLeft / (- s.totalFlow)
        return scalar
    
    def tick(s, New):
        new : GridState = New
        new.waterPercent = s.waterPercent
        scalar = s.calcWaterScalar()

        for pos in s.grid.adjacent(s.pos):
            adjacentstate = s.grid.Get(pos)
            scalar2 = min(adjacentstate.calcWaterScalar(), scalar)
            change = ((s.waterPercent + s.height) -
                    (adjacentstate.waterPercent + adjacentstate.height))/4
            change = max(min(change ,s.waterPercent),- adjacentstate.waterPercent)
            new.waterPercent -= change * scalar2

        if s.type == GridTypes.Plant:
            new.plantLife = s.plantLife - 0.05
            new.waterPercent -= (0.01 + random.random() * 0.005)
        
        if new.rainTime > 0:
            new.rainTime -= 1
            new.waterPercent += new.rainAmount

        new.waterPercent = max(min(new.waterPercent, 0.999 - s.height), 0)

        if (new.waterPercent < (random.random() / 10) or
                s.plantLife <= 0):
            new.removePlant()

    def canPlantMakeSapling(s, New, state):
        return (s.hasPlant and
                s.waterPercent >= 0.1 and
                New.waterPercent >= 0.1 and
                abs(s.height - state.height) < 0.4 and
                random.random() < 0.2)
    
    def plantMakeSapling(s, new):
        New : GridState = new
        New.waterPercent -= 0.1
    
    def canPlantGrow(s, Color : pg.Color):
        return not s.hasPlant
    

class GridBoard:
    nab = [(0, 1),(1, 0),(0, -1),(-1, 0)]#, (1, 6),(1, -1),(-1, -2),(-1, 5)]
    def __init__(s, width, height):
        s.board = []
        s.Width = width
        s.Height = height

        for x in range(width):
            row = []
            for y in range(height):
                row.append(GridState((x, y), s))
            s.board.append(row)

    def populate(s):
        
        for i in range(round(s.Width / 4)):
            startPos = (
            random.randint(0, s.Width - 1), random.randint(0, s.Height - 1))
            facing = math.radians(random.randint(0, 359))
            mountainrangeLength = random.randint(1, s.Width) * (random.random() / 4 + 0.75)
            mountainrangeLength = round(mountainrangeLength)

            poss: list[tuple[int, int]] = []
            currentPos = startPos
            for i in range(mountainrangeLength):
                x, y = round(currentPos[0]), round(currentPos[1])
                if (x, y) not in poss and random.random() < 0.9:
                    poss.append((x, y))

                facingVector = (math.cos(facing), math.sin(facing))
                facing += (random.random() - 0.5) / 3

                currentPos = addPos(currentPos, facingVector)

            neighbrous = []
            for pos in poss:
                for newPos in s.adjacent(pos):
                    if newPos not in poss:
                        neighbrous.append(newPos)
            
            for n in neighbrous:
                if random.random() < 0.7:
                    poss.append(n)
                for newPos in s.adjacent(n):
                    if (newPos not in poss
                    and newPos not in neighbrous
                    and random.random() < 0.5):
                        poss.append(newPos)

            for pos in poss:
                state: GridState = s.Get(s.wrap(pos))
                state.height += 0.3
                state.height = min(state.height, 0.9999)

        for pos in s:
            s.Get(pos).waterPercent = max(min(s.Get(pos).waterPercent, 1 - s.Get(pos).height), 0)
        for i in range(20):
            for pos in s:
                s.Get(pos).waterPreTick()

            for pos in s:
                s.Get(pos).tick(s.Get(pos))
                
        for pos in s:
            if (random.random() < 0.1):
                s.Get(pos).setPlant(pg.Color(random.randint(0, 100),
                                      random.randint(30, 200),
                                      random.randint(0, 50)), pos)

    def copy(s, subTick = False):
        grid = GridBoard(s.Width, s.Height)
        for pos in s:
            grid.Set(pos, s.Get(pos).copy(grid, subTick))
        return grid
    
    def contained(s, pos):
        return (0 <= pos[0]) and (pos[0] < s.Width) and (0 <= pos[1]) and (pos[1] < s.Height)

    def adjacent(s, pos):
        for a in GridBoard.nab:
            newPos = (pos[0] + a[0], pos[1] + a[1])
            newPos = s.wrap(newPos)
            if s.contained(newPos): yield newPos

    def wrap(s, pos):
        return (pos[0] % s.Width, pos[1] % s.Height)

    def Get(s, pos, y = None) -> GridState:
        if y is None:
            return s.board[pos[0]][pos[1]]
        return s.board[pos][y]

    def Set(s, pos, Value):
        s.board[pos[0]][pos[1]] = Value

    def __iter__(s):
        for a in range(s.Width):
            for b in range(s.Height):
                yield (a,b)