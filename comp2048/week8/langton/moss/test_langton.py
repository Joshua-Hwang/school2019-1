# -*- coding: utf-8 -*-
"""
Langton's ant script with animated evolution

Created on Thu May 02 12:54:00 2019

@author: joshua
"""
import langton

N = 1024
iterations = 100
#create the game of life object
#------------ original --------------
#states = {
#        0: "1L",
#        1: "0R",
#        }
#------------- symmetric -------------
#states = {
#        0: "1L",
#        1: "2L",
#        2: "3R",
#        3: "0R",
#        }
#----------- fills square ------------
states = {
        0: "1L",
        1: "2R",
        2: "3R",
        3: "4R",
        4: "5R",
        5: "6R",
        6: "7L",
        7: "8L",
        8: "0R",
        }
maxColor = max(states.keys())

life = langton.Ant(N, states=states)
life.evolve()
cells = life.getStates() #initial state


#-------------------------------
#plot cells
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()

plt.gray()

img = plt.imshow(cells, vmin=0, vmax=maxColor, animated=True)

def animate(i):
    """perform animation step"""
    global life
    
    for i in range(iterations):
        life.evolve()

    cellsUpdated = life.getStates()
    
    img.set_array(cellsUpdated)
    
    return img

interval = 1 #ms

#animate 24 frames with interval between them calling animate function at each frame
ani = animation.FuncAnimation(fig, animate, interval=interval)

plt.show()