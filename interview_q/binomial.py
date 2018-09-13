import numpy as np 
from functools import reduce

def main():
    p = np.random.binomial(1, 0.5, 1000)
    f = lambda x, y: 1 if x == y else 0
    print (reduce(f, p, 0))
    return

main()