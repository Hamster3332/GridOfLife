import random
import pygame as pg
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
        s.waterPercent: float = 0.5
        s.typeChanged = False
        s.rainAmount  = 0
        s.rainTime = 0
        #   Plant
        s.hasPlant = False ## coming soon
        s.parent: tuple[int, int] = pos
        s.color: pg.Color = pg.Color(99, 62, 32)
        s.plantLife = 0

        s.rainAmount  = 0
        s.rainTime = 0
    
    def copy(s, grid, subTick):
        state = GridState(s.pos, grid)
        #   General
        state.type = s.type
        state.waterPercent = s.waterPercent
        if subTick: state.typeChanged = s.typeChanged
        else: state.typeChanged = False
        state.rainAmount = s.rainAmount
        state.rainTime = s.rainTime
        #   Plant
        state.hasPlant = s.hasPlant
        state.parent = s.parent
        state.color = s.color
        state.plantLife = s.plantLife
        return state
    
    def setPlant(s, Color : pg.Color, parent : tuple[int, int] = (0, 0)):
        if True:#not s.typeChanged and not s.hasPlant:
            s.type = GridTypes.Plant
            s.hasPlant = True
            s.typeChanged = True
            s.plantLife = 1
            s.parent = parent
            s.color = Color
            return True
        return False
    
    def removePlant(s):
        if not s.typeChanged and s.hasPlant:
            s.type = GridTypes.Ground
            s.typeChanged = True
            s.hasPlant = False
            return True
        return False

    def tick(s, New):
        new : GridState = New
        new.waterPercent = s.waterPercent
        for pos in s.grid.adjacent(s.pos):
            new.waterPercent -= (s.waterPercent - s.grid.Get(pos).waterPercent)/4

        if s.type == GridTypes.Plant:
            new.plantLife = s.plantLife - 0.05
            new.waterPercent -= (0.01 + random.random() * 0.005)
        
        new.waterPercent = max(min(new.waterPercent,1),0)

        if (new.waterPercent < (random.random() / 10) or
                s.plantLife <= 0):
            new.removePlant()

    def canPlantMakeSapling(s, New):
        return (s.hasPlant and
                s.waterPercent >= 0.1 and
                New.waterPercent >= 0.1 and
                random.random() < 0.2 and False)
    
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
        for pos in s:
            if (random.random() < 0):
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