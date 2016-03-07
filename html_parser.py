from HTMLParser import HTMLParser

class MyParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.line = ""
		self.in_tr = False
		self.in_table = False

	def handle_starttag(self, tag, attrs):
		if self.in_table and tag == "tr":
			self.line = ""
			self.in_tr = True
		if tag=='a':
			for attr in attrs:
				if attr[0] == 'href':
					self.line += attr[1] + " "

	def handle_endtag(self, tag):
		if tag == 'tr':
			self.in_tr = False
		if len(self.line):
			print self.line
		elif tag == "table":
			self.in_table = False

	def handle_data(self, data):
		if data == "Website":
			self.in_table = 1
		elif self.in_tr:
			data = data.strip()
		if data:
			self.line += data.strip() + " "

myp = MyParser()
myp.feed(opt_lines)