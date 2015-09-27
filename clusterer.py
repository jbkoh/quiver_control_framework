from sklearn.cluster import KMeans
from sklearn import datasets
import csv
import matplotlib.pyplot as plt
import numpy as np


class Clusterer():
	zonelist = None
	datadir = 'data/'

	def __init__ (self):
		self.zonelist = self.csv2list('metadata/partialzonelist.csv')

	def csv2list(self, filename):
		outputList = list()
		with open(filename, 'r') as fp:
			reader = csv.reader(fp, delimiter=',')
			for row in reader:
				outputList.append(row[0])
		return outputList

	def cluster_kmeans(self, featDict):
		est= KMeans(n_clusters=2, init='k-means++', max_iter=1000)
		est.fit(featDict.values())
		labels = est.labels_
		print featDict.keys()
		print featDict
		print labels

		fig, axis = plt.subplots(1,1)
		x = list()
		y = list()
		for val in featDict.values():
			x.append(val[0])
			y.append(val[1])
		axis.scatter(x,y)
		plt.show()
