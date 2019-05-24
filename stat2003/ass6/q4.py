#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
np.random.seed(42069)

for i in range(2):
    Z = np.random.normal(size=101)
    X = np.zeros(101)

    for n in range(1,len(X)):
        X[n] = ((n-1)*X[n-1] + Z[n])/n
    plt.plot(X)
    plt.show()

