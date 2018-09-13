import numpy as np 

def main():
    zeros = np.zeros((5,5))
    print (zeros)
    u = np.matrix([[1, 2], [3, 4]])
    v = np.matrix([[5, 6], [7, 8]])
    print (u+v)
    return

main()