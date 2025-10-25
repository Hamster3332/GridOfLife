import random
import pygame as pg
class GridTypes:
    Ground = 0
    Plant = 1
    Animal = 2
    AnimalOnPlant = 3

class GridState:
    def __init__(s, pos: tuple[int, int] = (0, 0)):
        s.type = GridTypes.Ground
        s.Old: tuple[int, int] = pos
        s.Color: pg.Color = pg.Color(99, 62, 32)
        s.WaterPercent: float = random.random() / 2
    
    def tick(s, New,  data):
        if s.type == GridTypes.Plant:
            New.WaterPercent -= max(0.02 + random.random() * 0.02 + (s.Color.g )/500 - (s.Color.r)/500, 0.01)
        else:
            New.WaterPercent += 0.1
        New.WaterPercent = max(min(New.WaterPercent, 0.9), 0)
        if New.WaterPercent < random.random() / 4:
            New.type = GridTypes.Ground
            #New.Color = pg.Color(99, 62, 32)

    def canGrow(s, Color : pg.Color):
        return (s.type == GridTypes.Ground and
        s.WaterPercent > random.random() and
        (255 - (Color.r * random.random())) / 255 > s.WaterPercent)
    
    def copy(s):
        State = GridState()
        State.type = s.type
        State.Old = s.Old
        State.Color = s.Color
        State.WaterPercent = s.WaterPercent
        return State

class GridBoard:
    nab = [(0, 1),(1, 0),(0, -1),(-1, 0)]
    def __init__(s, width, height):
        s.board = []
        s.Width = width
        s.Height = height

        for x in range(width):
            row = []
            for y in range(height):
                row.append(GridState((x, y)))
            s.board.append(row)

    def populate(s):
        for pos in s:
            if (random.random() < 0.05):
                s.Get(pos).type = GridTypes.Plant
                s.Get(pos).Color = pg.Color(random.randint(0, 100),
                                      random.randint(30, 200),
                                      random.randint(0, 50))

    def copy(s):
        grid = GridBoard(s.Width, s.Height)
        for pos in s:
            grid.Set(pos, s.Get(pos).copy())
        return grid
    
    def contained(s, pos):
        return (0 <= pos[0]) and (pos[0] < s.Width) and (0 <= pos[1]) and (pos[1] < s.Height)

    def adjacent(s, pos):
        for a in GridBoard.nab:
            newPos = (pos[0] + a[0], pos[1] + a[1])
            newPos = s.wrap(newPos)
            if s.contained(newPos): yield newPos

    def wrap(s, pos):
        return ((pos[0] + s.Width) % s.Width, (pos[1] + s.Height) % s.Height)

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