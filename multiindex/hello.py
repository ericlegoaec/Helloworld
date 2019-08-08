
import os
import pandas as pd 

def main():
	tick_df = pd.read_excel(os.path.join(os.path.dirname(__file__), "hard core tick data.xlsx"), header=[0,1])
	# info_df = pd.read_excel(os.path.join(os.path.dirname(__file__), "additional data.xlsx"), index_col=None)

	print (tick_df.index.values)
	# print (info_df)
	return

if __name__ == "__main__":
	main()
