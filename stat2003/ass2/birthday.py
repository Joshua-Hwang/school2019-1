#!/bin/env python3
# Note: python2 works just as well

import random
SEED = 1

NUM_TESTS = 100000
NUM_DAYS = 365

def simulate_bday():
    # Create a generating list of birthdays
    birthdays = (random.randint(0,NUM_DAYS-1) for x in range(NUM_DAYS))
    birthday_counter = [0 for x in range(NUM_DAYS)]
    for birthday in birthdays:
        if birthday_counter[birthday] > 0:
            # This day has been counted before
            return sum(birthday_counter)
        birthday_counter[birthday] += 1

random.seed(SEED)
tests = [simulate_bday() for x in range(NUM_TESTS)]
mean = sum(tests)/float(len(tests))

print("Expectation:", mean)
