# -*- coding: utf-8 -*-
"""
Test script for running a Turing machine unary adder

Created on Fri Mar 29 21:57:42 2019

@author: shakes
"""
from turing_machine import TuringMachine

#create the Turing machine
multiplier = TuringMachine( 
    { 
        #'b' determines the tally we'll be applying it to those will get removed at the end but also
        #'a' the tallies on the right side we've already done and also the tallies we've manually placed
        #'X' the left end, treat it like another 1
        #'B' the left end, treat it like another b

        #0. Set left end to 'X' go to the right end
        #1. Turn first tally into 'a' then go to the left
        #2. Find first tally after 0
        #3. Set this tally to 'b' then go back right
        #4. Go all the way to the right and enter 'b' at the first empty space
        #5. Repeat 3 and 4 until the left side hits 'X'
        #5.5 Replace all 'b's on the left with 1s
        #6. Find the next tally and repeat from step 1
        #7. Stop once you can't find a tally (you hit the 0)
        #8. Clear left then clear right until you hit empty or 'b'

        ('q0', '1'): ('FindRightEnd', 'X', 'R'),
        ('q0', '0'): ('ClearRight', '', 'R'),

        ('FindRightEnd', '1'): ('FindRightEnd', '1', 'R'),
        ('FindRightEnd', '0'): ('FindRightEnd', '0', 'R'),
        ('FindRightEnd', ''): ('CheckLeftTally', '', 'L'),
        ('FindRightEnd', 'a'): ('CheckLeftTally', 'a', 'L'),

        ('CheckLeftTally', '0'): ('ClearFromLeft', '0', 'L'),
        ('CheckLeftTally', '1'): ('GetToZero', 'a', 'L'),

        ('GetToZero', '1'): ('GetToZero', '1', 'L'),
        ('GetToZero', 'a'): ('GetToZero', 'a', 'L'),
        ('GetToZero', 'b'): ('GetToZero', 'b', 'L'),
        ('GetToZero', '0'): ('FindLHSTally', '0', 'L'),

        ('FindLHSTally', '1'): ('AddTally', 'b', 'R'),
        ('FindLHSTally', 'b'): ('FindLHSTally', 'b', 'L'),
        ('FindLHSTally', 'X'): ('AddTally', 'B', 'R'),
        ('FindLHSTally', 'B'): ('BsToOnes', 'X', 'R'),

        ('AddTally', '1'): ('AddTally', '1', 'R'),
        ('AddTally', '0'): ('AddTally', '0', 'R'),
        ('AddTally', 'b'): ('AddTally', 'b', 'R'),
        ('AddTally', 'a'): ('AddTally', 'a', 'R'),
        ('AddTally', ''): ('GetToZero', 'b', 'L'),

        ('ClearFromLeft', '1'): ('ClearFromLeft', '1', 'L'),
        ('ClearFromLeft', 'X'): ('ClearRight', '', 'R'),
        ('ClearRight', 'a'): ('ClearRight', '' ,'R'),
        ('ClearRight', '1'): ('ClearRight', '' ,'R'),
        ('ClearRight', '0'): ('ClearRight', '' ,'R'),
        ('ClearRight', 'b'): ('BsToOnes' , '1', 'R'),
        ('ClearRight', ''): ('qa', '', 'R'),
        ('BsToOnes', 'b'): ('BsToOnes', '1', 'R'),
        ('BsToOnes', '0'): ('FindRightEnd', '0', 'R'),
        ('BsToOnes', ''): ('qa', '', 'R'),

        #Write your transition rules here as entries to a Python dictionary
        #For example, the key will be a pair (state, character)
        #The value will be the triple (next state, character to write, move head L or R)
        #such as ('q0', '1'): ('q1', '0', 'R'), which says if current state is q0 and 1 encountered
        #then transition to state q1, write a 0 and move head right.
    }
)

multiplier.debug('111011', step_limit=900)
