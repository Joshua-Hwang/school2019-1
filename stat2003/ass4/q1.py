#!/usr/bin/env python3
import random

# produces a result that could be produced from random variable X
def randX():
    U = random.random()
    X = (26*U + 1)**(2/3)
    return X

# the seed for reproducibility
random.seed(1337)
# NumSamples - number of simulations
NumSamples = 1000000

mean = sum(randX() for i in range(NumSamples))/NumSamples
print("The mean is:",mean)
