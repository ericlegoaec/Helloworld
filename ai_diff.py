import csv

def csv_to_arr(csv_file):
	arr = []
	with open(csv_file, 'rU') as f:
		reader = csv.reader(f)
		arr = list(reader)
	header = ','.join(arr[0])
	arr = arr[1:]
	#print header
	return header, arr

def arr_to_csv(file_name, header, data_arr):
	f1 = open(file_name, "w")
	f1.write(header+'\n')

	for data_row in data_arr:
		line = '' 
		for ele in data_row:
			line = line + str(ele) + ',' 

		line = line[:-1] + '\n'
		f1.write(line)    

	f1.close()
	return

f1 = open("D:\\book4.csv", "w")
txt_header, txt_arr = csv_to_arr("D:\\book2.txt")

for row in txt_arr:
	if len(row) > 0:
		f1.write(','.join(row[0].split(' ')) + '\n' )