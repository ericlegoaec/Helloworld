
import inspect
from dateclass import *
from market.marketutil import *
from schedule.scheduleutil import *

class TestDate():
	def __init__(self):

		return

	def __call__(self):
		dt2 = datetime.datetime(2019, 1, 31)

		py_dt = mydatetime.set_origin(datetime.datetime(1980, 12, 1))
		ql_dt = myqldatetime()
		
		print (py_dt.get_origin())
		print (ql_dt.get_origin())

		myqldatetime.set_origin(dt2)
		print (ql_dt.get_origin())
		return

def main():
	dt_now = datetime.datetime.now()
	Date.set_origin(dt_now.day, dt_now.month, dt_now.year)
	x = Market()
	eq_dic, vol_dic, rates_dic = x.get(".HSI", currency="", pct_strike=True, has_holiday=True)
	print (eq_dic)
	return

def test_init():
	dt1 = datetime.datetime(1970, 12, 31)
	# dt2 = datetime.datetime(2019, 1, 31)

	py_dt = mydatetime.set_origin(dt1)
	ql_dt = myqldatetime.set_origin(dt1)

	x = TestDate()
	x()
	return

test_init()
