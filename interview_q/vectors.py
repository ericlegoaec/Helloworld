
import numpy as np 
import quantmod as qm

symbols = ["BABA", "AAPL", "CSCO", "IBM"]
ret = lambda x: np.log(x) - np.log(x).shift(1)

def main():
	u = np.array([[4, 7], [-2, 6]])
	v = np.array([[0.6, -0.7], [-0.2, 0.4]])

	dfs = list(map(lambda x: qm.get_symbol(x).to_frame(), symbols))
	for df in dfs:
		df['log_ret'] = ret(df["Adj Close"])
	rets = [df.log_ret.mean(axis=0) for df in dfs]
	cv = np.cov(rets)
	print (cv)
	return
main()