import pygame as pg
import math


class Point:
    def __init__(s, x, y = 0):
        if isinstance (x, Point):
            s.x = x.x
            s.y = x.y
        else:
            s.x = x
            s.y = y

    def add(s, P):
        s.x += P[0]
        s.y += P[1]
        return s

    def Cadd(s, P):
        copy = Point(s)
        copy.x += P[0]
        copy.y += P[1]
        return copy
    
    def rotateAround(s, center, angle):
        cx = s.x - center[0]
        cy = s.y - center[1]

        x = math.cos(angle)
        y = -math.sin(angle)

        nx = cx * x - cy * y
        ny = cy * x + cx * y

        s.x = nx + center[0]
        s.y = ny + center[1]
        return s
    
    def __getitem__(s, key):
        return (s.x, s.y)[key]
    
    def get(s):
        return (s.x, s.y) 

class Rect:
    def __init__(s, x, y, width, height, border = 0, rotation = 0):
        s.y = y
        s.x = x
        s.width = width
        s.height = height
        s.borderR = border

        s.rotation = rotation
    
    def draw(s, window, color : pg.Color, border = None):
        s.borderR = border
        center = (s.x + (s.width/2), s.y + (s.height/2))
        topLeft = Point(s.x, s.y)
        topRight = topLeft.Cadd((s.width, 0))
        downLeft = topLeft.Cadd((0, s.height))
        downRight = topLeft.Cadd((s.width, s.height))
        pg.draw.polygon(window, color,[topLeft.Cadd((s.borderR, 0)).rotateAround(center, s.rotation).get(),
                                       topLeft.Cadd((0, s.borderR)).rotateAround(center, s.rotation).get(),

                                       downLeft.Cadd((0, -s.borderR)).rotateAround(center, s.rotation).get(),
                                       downLeft.Cadd((s.borderR, 0)).rotateAround(center, s.rotation).get(),

                                       downRight.Cadd((-s.borderR, 0)).rotateAround(center, s.rotation).get(),
                                       downRight.Cadd((0, -s.borderR)).rotateAround(center, s.rotation).get(),
                                       
                                       topRight.Cadd((0, s.borderR)).rotateAround(center, s.rotation).get(),
                                       topRight.Cadd((-s.borderR, 0)).rotateAround(center, s.rotation).get()
                                    ])
        if (border != 0 and border != None):
            pg.draw.circle(window, color, topLeft.add((s.borderR,s.borderR)).rotateAround(center, s.rotation).get(), s.borderR)
            pg.draw.circle(window, color, topRight.add((-s.borderR,s.borderR)).rotateAround(center, s.rotation).get(), s.borderR)
            pg.draw.circle(window, color, downRight.add((-s.borderR,-s.borderR)).rotateAround(center, s.rotation).get(), s.borderR)
            pg.draw.circle(window, color, downLeft.add((s.borderR,-s.borderR)).rotateAround(center, s.rotation).get(), s.borderR)

    def getCornerPoints(s):
        topLeft = Point(s.x, s.y)
        topRight = topLeft.Cadd((s.width, 0))
        downLeft = topLeft.Cadd((0, s.height))
        downRight = topLeft.Cadd((s.width, s.height))
        return [topLeft.get(), topRight.get(), downLeft.get(), downRight.get()]


class Polygon:
    def __init__(self, static_points, outer_points):
        if type(static_points) == Rect:
            self.static_points = static_points.getCornerPoints()
        else:
            self.static_points = static_points
        if type(outer_points) == Rect:
            self.points = outer_points.getCornerPoints()
        else:
            self.points = outer_points

    def draw(self, window, color : pg.Color):
        points = self.static_points + self.points
        pg.draw.polygon(window, color, self.static_points)