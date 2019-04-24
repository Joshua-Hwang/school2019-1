#!/usr/bin/env python3
import random

# the seed for reproducibility
random.seed(1337)
# NumSamples - number of simulations
NumSamples = 100000

ans = (max(random.random() for i in range(10)) for n in range(NumSamples))
mean = sum(ans)/NumSamples
print("The mean is:", mean)
print("Expected was:", 10/11)
