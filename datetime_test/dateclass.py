
import datetime
import QuantLib as ql

class Dt:
	def __init__(d):

		return
	
	def test(self):
		print ("Hello")
		return

class mydatetime(datetime.datetime):
	origin = None
	def __init__(self, year, month, day):
		return

	@classmethod
	def set_origin(cls, dt):
		cls.origin = dt
		return cls(dt.year, dt.month, dt.day)

	def get_origin(self):
		return self.origin


class myqldatetime(ql.Date):
	origin = None
	def __init__(self):

		return

	@classmethod
	def set_origin(cls, dt):
		cls.origin = ql.Date(dt.day, dt.month, dt.year)
		return cls

	def get_origin(self):
		return self.origin

