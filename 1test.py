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


cm.Wall.TEXTURES = [load_image('wall.bmp')]
a = cm.Wall((50, 50))
lines = a.get_lines()

tf=lines[0]
print(tf)

Ax = np.arange(0., 20., 1.)
Ay=get_ay(tf,Ax)
print(Ax,Ay)

plt.plot(Ax,Ay)
plt.show()
