#!/usr/bin/env python3
import random

# produces a result that could be produced from random variable X
def randX():
    U = random.random()
    X = (26*U + 1)**(2/3)
    return X

def randS():
    return sum(randX() for i in range(100))

# the seed for reproducibility
random.seed(1337)
# NumSamples - number of simulations
NumSamples = 10000

success = 0
for i in range(NumSamples):
    if randS() > 600:
        success += 1

print("Approx answer", success/NumSamples)
