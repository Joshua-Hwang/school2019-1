#!/usr/bin/env python3
import random
import matplotlib.pyplot as plt
import numpy as np

# if you land on a cell with a key you get sent to the value
snakes_ladders = {3:11, 13:4, 15:19, 17:10}
start = 1
win = 21 # greater or equal to 21

def run_game():
    location = start
    rolls = 0
    while location <= win:
        rolls += 1
        location += random.randint(1,6)
        # if not in dictionary then remain at location
        location = snakes_ladders.get(location, location)
    return rolls

# the seed for reproducibility
random.seed(1337)
# NumSamples - number of simulations
NumSamples = 10000

ans = [run_game() for n in range(NumSamples)]
mean = sum(ans)/NumSamples
print("The mean is:", mean)

ans = np.array(ans)
left_of_first_bin = ans.min() - 0.5
right_of_last_bin = ans.max() + 0.5
plt.hist(ans,np.arange(left_of_first_bin, right_of_last_bin+1,1),density=True)
plt.show()
