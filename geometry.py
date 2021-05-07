import math

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def distance_to_line(self, line):
        perpendicular = abs(line.a * self.x + line.b * self.y + line.c) / \
            math.sqrt(line.a * line.a + line.b * line.b + line.c * line.c)
        return perpendicular

class Line:
    def __init__(self, p1, p2):
        if p1.y == p2.y:
            self.a = 0
            self.b = 1
            self.c = -p1.y
        else:
            self.a = 1
            self.b = -self.a * (p2.x - p1.x) / (p2.y - p1.y)
            self.c = -self.a * p1.x - self.b * p1.y

def squared_distance(p1, p2):
    return (p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y)

def distance(p1, p2):
    return math.sqrt(squared_distance(p1, p2))

def segments_intersect(p1, p2, p3, p4):
    # not accounting for the three-on-a-line cases
    l1 = Line(p1, p2)
    l2 = Line(p3, p4)

    if abs(l1.a * l2.b - l2.a * l1.b) < 1e-5:
        # parallel
        if abs(l1.b) < 1e-5:
            # vertical
            return min(max(p1.y, p2.y), max(p3.y, p4.y)) > \
                   max(min(p1.y, p2.y), min(p3.y, p4.y))
        if abs(l2.c / l2.b - l1.c / l1.b) >= 1e-5:
            return False
        else:
            return min(max(p1.x, p2.x), max(p3.x, p4.x)) > \
                   max(min(p1.x, p2.x), min(p3.x, p4.x))
    else:
        # intersection point; Cramer's rule
        D = l1.a * l2.b - l1.b * l2.a
        Dx = l1.b * l2.c - l1.c * l2.b
        Dy = l1.c * l2.a - l1.a * l2.c
        x = Dx / D
        y = Dy / D

        in_first = False
        in_second = False

        if abs(l1.b) < 1e-5:
            # l1 is vertical
            in_first = (y - p1.y) * (y - p2.y) < 0
        else:
            in_first = (x - p1.x) * (x - p2.x) < 0

        if abs(l2.b) < 1e-5:
            # l2 is vertical
            in_second = (y - p3.y) * (y - p4.y) < 0
        else:
            in_second = (x - p3.x) * (x - p4.x) < 0

        return in_first and in_second
