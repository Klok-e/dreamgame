# import ai_geneticNN as aign
import classMap as cm
from locals import *
import numpy as np
import matplotlib.pyplot as plt
import math


# a=aign.Ai()

# a.print_network()


def get_ay(txtF: str, Ax):
    Ay = []
    print(txtF)
    for x in Ax:
        y = eval(txtF)
        #print(x)
        Ay.append(y)
    return Ay

def c_tst():
    f1='-0.000000*x + 50.000000'
    f2='1*x + 40.000000'
    a=find_intersection_point(f1,f2)
    print(a)

    Ax = np.arange(0., 20., 1.)
    Ay1 = get_ay(f1, Ax)
    Ay2=get_ay(f2,Ax)

    plt.plot(Ax, Ay1,'bo',Ax,Ay2,'--r')
    plt.show()

#c_tst()

def tst():
    cm.Wall.TEXTURES = [load_image('wall.bmp')]
    a = cm.Wall((50, 50))

    ar=find_intersection_line_coll('1*x + 40.000000',a)
    print(ar)


    Ax = np.arange(0., 120., 1.)


    plt.show()

tst()