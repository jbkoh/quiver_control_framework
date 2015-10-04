import csv	

def csv2list(filename):
	outputList = list()
	with open(filename, 'r') as fp:
		reader = csv.reader(fp, delimiter=',')
		for row in reader:
			outputList.append(row[0])
	return outputList


def list2csv(data, filename):
	with open(filename, 'wb') as fp:
		writer = csv.writer(fp, delimiter='\n')
		writer.writerow(data)

	
