import pygame
import time
import classMap as m
# from classMap import *
import numpy as np
import math

BLACK = (0, 0, 0)
ORANGE = (255, 174, 53)
GREEN = (43, 255, 13)
DARKGREEN = (0, 134, 6)
GRAY = (218, 220, 214)
SCREENRECT = pygame.Rect(0, 0, 800, 500)

TILESIZE = (16, 16)
MAPSIZE = (100, 60)

FPS = 30
PHYSICS_FPS = 30

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
    k = (y1 - y2) / (x1 - x2)
    b = y2 - k * x2
    return "%f*x + %f" % (k, b)


def get_points_on_line(start, end, amount):
    # TODO: this
    return None


def is_point_in_collideble(point, coll):
    if isinstance(coll, m.Wall):  # do wall stuff
        a = coll.rect.collidepoint(point)
        return a
    elif isinstance(coll, m.Entity):  # do circle stuff
        p = coll.for_movement_struct['pos']
        r = coll.radius
        x1, y1 = p
        x2, y2 = point
        vx, vy = (x2 - x1, y2 - y1)
        mod = math.sqrt(vx ** 2 + vy ** 2)
        a = mod < r
        return a
    assert isinstance(coll, m.Wall) or isinstance(coll, m.Entity), 'not collideble'


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
