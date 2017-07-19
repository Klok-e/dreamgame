import classMap as cm
from locals import *
import numpy as np
import matplotlib.pyplot as plt
import math
import ai_geneticNN as aig


# a=aign.Ai()

# a.print_network()


def get_ay(txtF: str, Ax):
    Ay = []
    print(txtF)
    for x in Ax:
        y = eval(txtF)
        # print(x)
        Ay.append(y)
    return Ay


def c_tst():
    f1 = '-0.000000*x + 50.000000'
    f2 = '1*x + 40.000000'
    a = find_intersection_point(f1, f2)
    print(a)

    Ax = np.arange(0., 20., 1.)
    Ay1 = get_ay(f1, Ax)
    Ay2 = get_ay(f2, Ax)

    plt.plot(Ax, Ay1, 'bo', Ax, Ay2, '--r')
    plt.show()


# c_tst()

def tst():
    cm.Wall.TEXTURES = [load_image('wall.bmp')]
    a = cm.Wall((50, 50))

    nnn = round(-5.8600567268337203e+18)
    print(nnn)
    ar = is_point_in_collideble((358.82498566694153, nnn), a)
    print(ar)


# tst()

def tst10():
    a = degrees_for_sight_lines(40, 10, 5)
    print(a)


# tst10()

def tst11():
    a = points_on_line((10, 10), (10, 64), 10)
    print(a)


# tst11()

def tst12():
    n = aig.Agent()

    # tst12()
