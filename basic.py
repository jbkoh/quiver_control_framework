import csv	

def csv2list(self, filename):
	outputList = list()
	with open(filename, 'r') as fp:
		reader = csv.reader(fp, delimiter=',')
		for row in reader:
			outputList.append(row[0])
	return outputList
