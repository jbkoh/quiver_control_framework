from sklearn.cluster import KMeans
from sklearn import datasets
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pprint


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
		est= KMeans(n_clusters=4, init='k-means++', max_iter=1000)
		est.fit(featDict.values())
		labels = est.labels_
		print featDict.keys()
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(featDict)
		print labels
		print labels[featDict.keys().index('RM-4132')]

		fig, axis = plt.subplots(1,1)
		x = list()
		y = list()
		z = list()
		for zone, val in featDict.iteritems():
			if zone=='RM-4132':
				continue
			x.append(val[0])
			y.append(val[1])
			z.append(val[2])
		axis.scatter(x,y)
		axis.scatter(featDict['RM-4132'][0],featDict['RM-4132'][1],color='r')

		fig = plt.figure()
		ax = fig.add_subplot(111,projection='3d')
		ax.scatter(x,y,z)
		ax.scatter(featDict['RM-4132'][0], featDict['RM-4132'][1], featDict['RM-4132'][2], color='r')

		plt.show()
