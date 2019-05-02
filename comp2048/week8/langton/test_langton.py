# -*- coding: utf-8 -*-
"""
Langton's ant script with animated evolution

Created on Thu May 02 12:54:00 2019

@author: joshau
"""
import langton

N = 64

#create the game of life object
life = langton.Ant(N)
board = life.getGrid() #initial state

#-------------------------------
#plot cells
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()

plt.gray()

img = plt.imshow(board, animated=True)

def animate(i):
    """perform animation step"""
    global life
    
    life.evolve()
    boardUpdated = life.getGrid()
    
    img.set_array(boardUpdated)
    
    return img

interval = 200 #ms

#animate 24 frames with interval between them calling animate function at each frame
ani = animation.FuncAnimation(fig, animate, frames=24, interval=interval, blit=True)

plt.show()
