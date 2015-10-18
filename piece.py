from __future__ import division, print_function, absolute_import

from sklearn.metrics import mean_squared_error
from numpy.testing import assert_almost_equal, assert_array_equal, \
		TestCase, run_module_suite, assert_allclose, assert_equal
from scipy.interpolate import KroghInterpolator, krogh_interpolate, \
		BarycentricInterpolator, barycentric_interpolate, \
		PiecewisePolynomial, piecewise_polynomial_interpolate, \
		approximate_taylor_polynomial, pchip
import pywt
from scipy.interpolate import interp1d
#from scipy.lib.six.moves import xrange
from six.moves import xrange
import scipy
import numpy as np
from scipy.interpolate import splrep, splev
import pickle
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from math import sqrt
from copy import deepcopy
from numpy.matlib import repmat

with open('data\oneday_2150_0914.pkl') as fp:
	data = pickle.load(fp)
flow = data['Actual Supply Flow']
sp = data['Actual Sup Flow SP']

#with open('data\col_cs_4132_1014.pkl') as fp:
#	data = pickle.load(fp)
#data = data['RM-4132']
#flow = data['Actual Supply Flow'][50:-1]
#sp = data['Actual Sup Flow SP'][50:-1]
	
#tck = splrep(range(0,len(flow)), flow,s=0)
#test_xs = np.linspace(-1,700,20)
#spline_ys = splev(test_xs, tck)
#spline_yps = splev(test_xs, tck, der=1)
#xi = np.unique(tck[0])
#yi = [[splev(x, tck, der=j) for j in xrange(3)] for x in xi]
#P = PiecewisePolynomial(xi,yi)
#plt.plot(test_xs,P(test_xs), range(0,len(flow)), flow)
#plt.show()



#tck = splrep(range(0,len(flow)), flow,s=0)
#test_xs = np.linspace(-1,len(flow),20)
#spline_ys = splev(test_xs, tck)
#spline_yps = splev(test_xs, tck, der=1)
#xi = np.unique(tck[0])
#yi = [[splev(x, tck, der=j) for j in xrange(3)] for x in xi]
#P = PiecewisePolynomial(xi,yi,orders=1)
##plt.plot(test_xs,P(test_xs), range(0,len(flow)), flow)
#test_ys = P(test_xs)
#
#plot_x = np.linspace(0,len(flow)-1,len(flow))
#f = interp1d(test_xs,test_ys)
#plt.plot(plot_x, f(plot_x), range(0,len(flow)),flow)
#plt.show()
#
#tck = splrep(range(0,len(sp)), sp,s=0)
#test_xs = np.linspace(-1,700,20)
#spline_ys = splev(test_xs, tck)
#spline_yps = splev(test_xs, tck, der=0)
#xi = np.unique(tck[0])
#yi = [[splev(x, tck, der=j) for j in xrange(3)] for x in xi]
#P = PiecewisePolynomial(xi,yi,orders=0)
#plt.plot(test_xs,P(test_xs), range(0,len(sp)), sp)
#plt.show()

# EXAMPLE of wavelet transform
#cA, cD = pywt.dwt(flow, 'db1')
#inverted = pywt.idwt(cA[0:30], cD[0:30], 'db1')

def interp0(test_xs, test_ys, orig_x):
	d_xs = list()
	for x in test_xs[:-1]:
		idx = int(np.where(test_xs==x)[0])
		d_xs.append((test_ys[idx+1] - test_ys[idx])/(test_xs[idx+1]-x))
	plot_y = list()
	for x in orig_x[:-1]:
		idx = np.where(test_xs<=x)[0][-1]
#	idx = test_xs[(test_xs<=x)]x
#		plot_y.append((x-test_xs[idx])*d_xs[idx]+test_ys[idx])
		plot_y.append(test_ys[idx])
	plot_y.append(test_ys[-1])
	return plot_y

def interp1(test_xs, test_ys, orig_x):
	inter_f = interp1d(test_xs,test_ys)
	inter_y = inter_f(orig_x)
	return inter_y

def calc_noise_deprecated(data, N=20):
	orig_x = range(0,len(data))
	tck = splrep(orig_x, data,s=0)
	test_xs = np.linspace(0,len(data),N)
	spline_ys = splev(test_xs, tck)
	spline_yps = splev(test_xs, tck, der=1)
	xi = np.unique(tck[0])
	yi = [[splev(x, tck, der=j) for j in xrange(3)] for x in xi]
	P = PiecewisePolynomial(xi,yi,orders=0)
	#plt.plot(test_xs,P(test_xs), range(0,len(data)), data)
	test_ys = P(test_xs)

	#inter_f = interp1d(test_xs,test_ys)
	#inter_y = inter_f(orig_x)
	inter_y = interp0(test_xs, test_ys, orig_x)
	plt.plot(orig_x, data, orig_x, inter_y)
	plt.show()
	rmse = sqrt(mean_squared_error(inter_y, data))
	return rmse

def paa(data, numCoeff=10):
	data = data[:int(len(data)/numCoeff)*numCoeff]
	origData = deepcopy(data)
	N = len(data)
	segLen = int(N/numCoeff)
	sN = np.reshape(data, (numCoeff, segLen))
	g = lambda data: np.mean(data)
#	avg = np.mean(sN)
	avg = map(g,sN)
	data = np.matlib.repmat(avg, segLen, 1)
	data = data.ravel(order='F')
	plt.plot(data)
	plt.plot(origData)
	plt.show()
	rmse = sqrt(mean_squared_error(data, origData))
	return rmse

print(str(paa(sp)))
print(str(paa(flow)))
#print(str(calc_noise(flow, N=10)))
#print(str(calc_noise(sp, N=10)))
