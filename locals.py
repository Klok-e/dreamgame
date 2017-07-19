import pygame
import time
import classMap as m

import numpy as np
import math


BLACK = (0, 0, 0)
ORANGE = (255, 174, 53)
GREEN = (43, 255, 13)
DARKGREEN = (0, 134, 6)
GRAY = (218, 220, 214)
SCREENRECT = pygame.Rect(0, 0, 800, 500)

TILESIZE = (16, 16)
MAPSIZE = (50, 30)

FPS = 30
PHYSICS_FPS = 30  # TODO: implement this

threads=[]

dbg_clock = time.time()

ATTACK = 'ATTACK'
K_UP = 'K_UP'
K_LEFT = 'K_LEFT'
K_RIGHT = 'K_RIGHT'
STAY = 'STAY'
EAT = 'EAT'
action_choices = [ATTACK, K_UP, K_LEFT, K_RIGHT, STAY, EAT]


def load_image(file):
    "loads an image, prepares it for play"
    surface = pygame.image.load('images/' + file)
    # surface=surface.convert()
    return surface


def debug_param(*params):
    global dbg_clock
    if time.time() - dbg_clock > 0.3:
        dbg_clock = time.time()
        print(*params)


def line_eq(xy1, xy2):
    # print("Координаты точки A(x1;y1):")
    x1 = xy1[0]
    y1 = xy1[1]

    # print("Координаты точки B(x2;y2):")
    x2 = xy2[0]
    y2 = xy2[1]

    # print("Уравнение прямой, проходящей через эти точки:")
    if round(x1,5) == round(x2,5):
        #print('asddgwrsds')
        return float(x1)
    k = (y1 - y2) / (x1 - x2)
    b = y2 - k * x2
    return "%f*x + %f" % (k, b)


def points_on_line(start, end, amount):
    dist = dist_between_points(start, end)

    point_diff = dist / amount

    x1, y1 = start
    x2, y2 = end
    ang = math.atan2(y2 - y1, x2 - x1)

    x_diff = math.cos(ang) * point_diff

    points = np.empty((amount, 2))

    eq = line_eq(start, end)
    if isinstance(eq, float):
        curry = y1
        for i in range(amount):
            points[i][0] = x1
            points[i][1] = curry
            curry += point_diff
        #print(points,'-points')
        return points

    currx = x1
    for i in range(amount):
        x = currx

        y = eval(eq)
        points[i][1] = y
        points[i][0] = currx
        currx += x_diff
    # print(points.dtype)
    return points


def degrees_for_sight_lines(initial_degree, step, amount):
    assert amount % 2 == 1, 'amount is even'

    a = []
    mul = 0
    for i in range(amount):
        if i % 2 == 0:
            a.append(initial_degree - step * mul)
        elif i % 2 == 1:
            mul += 1
            a.append(initial_degree + step * mul)
    a.sort()
    return a


def dist_between_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    vx, vy = (x2 - x1, y2 - y1)
    mod = math.sqrt(vx ** 2 + vy ** 2)
    return mod


def is_point_in_collideble(point, coll):
    assert isinstance(coll, m.Wall) or isinstance(coll, m.Entity), 'not collideble'
    assert isinstance(point, tuple) or isinstance(point, list), 'not tuple or list'
    # point=round(point[0]),round(point[1])
    # print(type(point[0]),type(point[1]))
    if isinstance(coll, m.Wall):  # do wall stuff
        a = coll.rect.collidepoint(point)

        return a
    elif isinstance(coll, m.Entity):  # do circle stuff
        p = coll.for_movement_struct['pos']
        r = coll.radius
        a = dist_between_points(p, point) < r
        return a


# TODO: make obstacle detection mathematically
def find_intersection_point(line1_or_int, line2: str):
    if isinstance(line1_or_int, str) and isinstance(line2, str):
        assert isinstance(line1_or_int, str) and isinstance(line2, str), 'not str'

        line1 = line1_or_int.split(' + ')
        k1 = float(line1[0].split('*')[0])
        b1 = float(line1[1])

        line2 = line2.split(' + ')
        k2 = float(line2[0].split('*')[0])
        b2 = float(line2[1])

        assert k1 != k2, 'oh shi 1/0'
        x = (b2 - b1) / (k1 - k2)

        y = eval(line1_or_int)  # x in random lline eq = y
        assert isinstance(y, float), 'not a number'

        return x, y
    elif isinstance(line1_or_int, int) and isinstance(line2, str):
        x = line1_or_int
        y = eval(line2)
        return x, y

    assert isinstance(line1_or_int, int) and isinstance(line2, str), 'not int or not str'


def find_intersection_line_coll(line: str, coll):
    if isinstance(coll, m.Wall):  # do wall stuff
        coords = []  # number of square's sides xes
        # print(coords)
        for i, eq in enumerate(coll.line_equations):
            coords.append(find_intersection_point(eq, line))
        # print(coords)


        # check domain
        colliding = []
        for x, y in coords:
            a = coll.rect.collidepoint(x, y)
            colliding.append(a)

        ans = zip(coords, colliding)
        print(list(ans))
        return ans

    elif isinstance(coll, m.Entity):  # do circle stuff
        p = coll.for_movement_struct['pos']
        r = coll.radius
