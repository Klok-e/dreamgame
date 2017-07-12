import pygame
import time

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

def line_eq(xy1,xy2):
    #print("Координаты точки A(x1;y1):")
    x1 = xy1[0]
    y1 = xy1[1]

    #print("Координаты точки B(x2;y2):")
    x2 = xy2[0]
    y2 = xy2[1]

    #print("Уравнение прямой, проходящей через эти точки:")
    k = (y1 - y2) / (x1 - x2)
    b = y2 - k * x2
    return "%f*x + %f" % (k, b)