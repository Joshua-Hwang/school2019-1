# -*- coding: utf-8 -*-
"""
Langton's ant module

This module defines the classes required for Langton's ant.
Based on Game of Life module

Created on Tue Apr 30 15:09:00 2019

@author: joshua
"""
import numpy as np
from scipy import signal

# need math
import math

class Ant:
    '''
    Object for computing Langton's ant
    '''
    def __init__(self, N=256, finite=False, states=None):
        self.grid = np.zeros((N,N), np.uint)
        self.finite = finite
        self.ant = np.array([math.ceil(N/2), math.ceil(N/2)], np.uint)
        # rotation {N:0, E:1, S:2, W:3}
        self.rotation = 0
        if states:
            self.states = states
        else:
            self.states = {
                    0: "1L",
                    1: "0R",
                    }
        
    def getState(self):
        return self.grid[self.ant[0], self.ant[1]]
    
    def getStates(self):
        '''
        Returns the current states of the cells
        '''
        return self.grid
        
    def getGrid(self):
        '''
        Same as getStates()
        '''
        return self.getStates()
               
    def evolve(self):
        '''
        Langton's ant rules:
        If on white square, toggle the colour and move to the right (right of ant)
        If on black square, toggle the colour and move to the left (left of ant)
        '''
        operation = self.states[self.getState()]
        # change colour
        self.grid[self.ant[0], self.ant[1]] = int(operation[:-1])
        # rotate
        self.rotation += 4 + (1 if operation[-1] == 'R' else -1)
        self.rotation = self.rotation % 4
        # move
        self.move()

    def move(self):
        # checks rotation and changes ant variable
        self.ant += {
            0: np.array([0,1], np.uint),
            1: np.array([1,0], np.uint),
            2: np.array([0,-1], np.uint),
            3: np.array([-1,0], np.uint),
            }[self.rotation]
