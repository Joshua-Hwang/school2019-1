# -*- coding: utf-8 -*-
"""
Busy beaver Turing machine with 2 states.

Created on Sat Mar 30 13:55:25 2019

@author: shakes
"""
from turing_machine import TuringMachine


#create the Turing machine
bbeaver = TuringMachine( 
    { 
        #Write your transition rules here as entries to a Python dictionary
        #For example, the key will be a pair (state, character)
        #The value will be the triple (next state, character to write, move head L or R)
        #such as ('q0', '1'): ('q1', '0', 'R'), which says if current state is q0 and 1 encountered
        #then transition to state q1, write a 0 and move head right.
        ## 2 card = 4 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('b', '1', 'L'),
        #('b', '0'): ('a', '1', 'L'),
        #('b', '1'): ('h', '1', 'R'),
        ## 3 card - suboptimal = 5 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('b', '1', 'L'),
        #('b', '0'): ('a', '1', 'L'),
        #('b', '1'): ('c', '1', 'R'),
        #('c', '0'): ('h', '1', 'L'),
        #('c', '1'): ('b', '1', 'R'),
        ## 3 card = 6 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('c', '1', 'L'),
        #('b', '0'): ('a', '1', 'L'),
        #('b', '1'): ('b', '1', 'R'),
        #('c', '0'): ('b', '1', 'L'),
        #('c', '1'): ('h', '1', 'R'),
        ## 4 card - suboptimal = 7 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('d', '1', 'L'),
        #('b', '0'): ('a', '1', 'L'),
        #('b', '1'): ('b', '1', 'R'),
        #('c', '0'): ('b', '1', 'L'),
        #('c', '1'): ('c', '1', 'R'),
        #('d', '0'): ('c', '1', 'L'),
        #('d', '1'): ('h', '1', 'R'),
        ## 4 card = 13 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('c', '0', 'R'),
        #('b', '0'): ('a', '1', 'L'),
        #('b', '1'): ('a', '1', 'R'),
        #('c', '0'): ('h', '1', 'R'),
        #('c', '1'): ('d', '1', 'R'),
        #('d', '0'): ('d', '1', 'L'),
        #('d', '1'): ('b', '0', 'L'),
        ## 5 card - suboptimal = 14 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('c', '0', 'R'),
        #('b', '0'): ('a', '1', 'L'),
        #('b', '1'): ('a', '1', 'R'),
        #('c', '0'): ('e', '1', 'R'),
        #('c', '1'): ('d', '1', 'R'),
        #('d', '0'): ('d', '1', 'L'),
        #('d', '1'): ('b', '0', 'L'),
        #('e', '0'): ('e', '1', 'L'),
        #('e', '1'): ('h', '1', 'L'),
        ## 5 card = 4098 ##
        #('a', '0'): ('b', '1', 'R'),
        #('a', '1'): ('c', '1', 'L'),
        #('b', '0'): ('c', '1', 'R'),
        #('b', '1'): ('b', '1', 'R'),
        #('c', '0'): ('d', '1', 'R'),
        #('c', '1'): ('e', '0', 'L'),
        #('d', '0'): ('a', '1', 'L'),
        #('d', '1'): ('d', '1', 'L'),
        #('e', '0'): ('h', '1', 'R'),
        #('e', '1'): ('a', '0', 'L'),
    },
    start_state='a', accept_state='h', reject_state='r', blank_symbol='0'
)

bbeaver.debug('00000000000000', step_limit=1000)
