import math

def easeInOutSine(x: float) -> float:
    if (x <= 0):
        return 0
    return -(math.cos(math.pi * x) - 1) / 2

def f(x : float) -> float:
    return math.pow(x, 2) * (3 - 2 * x)

def easeInCubic(x: float) -> float:
    return x * x * x

def easeOutCubic(x: float) -> float:
    return 1 - math.pow(1 - x, 3)

def lerp(a, b, lerp):
    if lerp < 0 : return a
    if lerp > 1 : return b
    return a + (b - a)* lerp

def lerpPos(a, b, Lerp):
    return (lerp(a[0], b[0], Lerp), lerp(a[1], b[1], Lerp))

def addPos(pointA: tuple[int, int], pointB : tuple[int, int]) -> tuple[int, int]:
    return (pointA[0] + pointB[0], pointA[1] + pointB[1])

def subPos(pointA: tuple[int, int], pointB : tuple[int, int]) -> tuple[int, int]:
    return (pointA[0] - pointB[0], pointA[1] - pointB[1])

def manhattanDistance(pointA: tuple[int, int], pointB : tuple[int, int]) -> int:
    return abs(pointA[0]-pointB[0]) + abs(pointA[1]-pointB[1])

def easeOutBounce(x: float) -> float:
    n1 = 7.5625
    d1 = 2.75
    
    if (x <= 0):
        return 0
    if (x < 1 / d1):
        return n1 * x * x
    elif (x < 2 / d1):
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    elif (x < 2.5 / d1):
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    else:
        x -= 2.625 / d1
        return n1 * x * x + 0.984375

class Rectangle():
    pass

if __name__ == "__main__":
    print(easeOutBounce(0.0))
    print(easeOutBounce(0.1))
    print(easeOutBounce(0.2))
    print(easeOutBounce(0.3))
    print(easeOutBounce(0.4))
    print(easeOutBounce(0.5))
    print(easeOutBounce(0.6))
    print(easeOutBounce(0.7))
    print(easeOutBounce(0.8))
    print(easeOutBounce(0.9))
    print(easeOutBounce(1))