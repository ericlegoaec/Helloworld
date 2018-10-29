import numpy as np
# import pandas as pd
# import pandas_datareader as pdr
# from scipy import stats
import matplotlib.pyplot as plt
# import seaborn as sns

np.random.seed(20)

def bsm_call(S_t, K, r, vol, T, t=0):
	den = 1 / (vol * np.sqrt(T - t))
	d1 = den * (np.log(S_t / K) + (r + 0.5 * vol ** 2) * (T - t))
	d2 = den * (np.log(S_t / K) + (r - 0.5 * vol ** 2) * (T - t))
	C = S_t * stats.norm.cdf(d1) \
	- K * np.exp(-r * (T - t)) * stats.norm.cdf(d2)
	return C

def bsm_call_mc(S_0, K, r, vol, T):
	# Number of time steps for simulation
	n_steps = int(T * 252)
	# Time interval
	dt = T / n_steps
	# Number of simulations
	N = 100000
	# Zero array to store values (often faster than appending)
	S = np.zeros((n_steps, N))
	S[0] = S_0

	for t in range(n_steps-1):
		# Draw random values to simulate Brownian motion
		Z = np.random.standard_normal(N)
		S[t+1] = S[t] * np.exp((r - 0.5 * vol ** 2) * dt + (vol * np.sqrt(dt) * Z))

	# Sum and discount values
	C = np.exp(-r * T) * 1 / N * np.sum(np.maximum(S[-1] - K, 0))
	# plt.figure(figsize=(12,8))
	# plt.plot(S[:,0:50])
	# plt.axhline(K, c="k", xmin=0,
	# 			xmax=n_steps,
	# 		label="Strike Price")
	# plt.xlim([0, n_steps])
	# plt.ylabel("Non-Discounted Value")
	# plt.xlabel("Time step")
	# plt.title("First 50 Option Paths")
	# plt.legend(loc="best")
	# plt.show()
	return C


# Parameters - same values as used in the example above 
# repeated here for a reminder, change as you like
# Initial asset price
S_0 = 100
# Strike price for call option
K = 110
# Time to maturity in years
T = 0.5
# Risk-free rate of interest
r = 0.03
# Historical Volatility
vol = 0.5

# C_bsm = bsm_call(S_0, K, r, vol, T)
C = bsm_call_mc(S_0, K, r, vol, T)

print("Strike price: {:.2f}".format(K))
# print("BSM Option Value Estimate: {:.2f}".format(C_bsm))
print("Monte Carlo Option Value Estimate: {:.2f}".format(C))


