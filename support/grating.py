import numpy as np
import matplotlib.pyplot as plt
import external as ex
ex = reload(ex)

def gabor(size=28, lambda_freq=5, theta=0, sigma=5, phase=0, noise=0):
	"""
	Creates a Gabor patch

	Args:

		size (int): Image side
		lambda_freq (int or float): Spatial frequency (pixels per cycle) 
		theta (int, float, list or numpy array): Grating orientation in degrees (if list or array, a patch is created for each value)
		sigma (int or float): gaussian standard deviation (in pixels)
		phase (float, list or numpy array): phase of the filter; range: [0, 1]
		noise (int): noise level to add to Gabor patch; represents the standard deviation of the Gaussian distribution from which noise is drawn; range: (0, inf

	Returns:
		(1D or 2D numpy array): 1D or 2D Gabor patch (n images * n pixels)
	"""
	#normalize input parameters
	noise = np.clip(noise, 1e-10, np.inf)
	if type(theta) == int or type(theta) == float: theta = np.array([theta])
	elif type(theta) == list: theta = np.array(theta)
	if type(phase)==float or type(phase)==int: phase = np.array([phase])
	n_gratings = len(theta)

	# make linear ramp
	X0 = (np.linspace(1, size, size) / size) - .5

	# Set wavelength and phase
	freq = size / float(lambda_freq)
	phaseRad = phase * 2 * np.pi

	# Make 2D grating
	Xm, Ym = np.meshgrid(X0, X0)
	Xm = np.tile(Xm, (n_gratings, 1, 1))
	Ym = np.tile(Ym, (n_gratings, 1, 1))

	# Change orientation by adding Xm and Ym together in different proportions
	thetaRad = (theta / 360.) * 2 * np.pi
	Xt = Xm * np.cos(thetaRad)[:,np.newaxis,np.newaxis]
	Yt = Ym * np.sin(thetaRad)[:,np.newaxis,np.newaxis]

	# 2D Gaussian distribution
	gauss = np.exp(-((Xm ** 2) + (Ym ** 2)) / (2 * (sigma / float(size)) ** 2))

	gratings = np.sin(((Xt + Yt) * freq * 2 * np.pi) + phaseRad[:,np.newaxis,np.newaxis])
	gratings *= gauss #add Gaussian
	gratings += np.random.normal(0.0, noise, size=np.shape(gratings)) #add Gaussian noise
	gratings -= np.min(gratings)

	gratings = np.reshape(gratings, (n_gratings, size**2))

	return gratings

def tuning_curves(W, method, output, params=None):
	"""
	compute the tuning curve of the neurons

	Args:
		W (dict): dictionary of weight matrices (each element of the dictionary is a weight matrix from an individual run)
		method (str): way of computing the tuning curves. Can be: 'basic' (w/o noise, w/ softmax), 'no_softmax' (w/o noise, w/o softmax), 'with_noise' (w/ noise, w/ softmax)
		output (bool): whether or not to generate plots
		params (dict, optional): parameters of the main simulation (kwargs)

	returns:
		(dict): the tuning curves for each neuron of each run
	"""

	if method not in ['basic', 'no_softmax', 'with_noise']:
		print '!!! invalid method - using \'basic\' method !!!'
		method='basic'

	if params is not None:
		t = params['t_hid']
		target_ori = params['target_ori']

	else:
		t = 0.1
		target_ori = 45.


	noise = 1.0
	noise_trial = 100
	ori_step = 0.1
	n_input = int(180/ori_step)
	im_size = int(np.sqrt(np.size(W[W.keys()[0]],0)))
	n_neurons = int(np.size(W[W.keys()[0]],1))

	orientations = np.arange(0,180,ori_step)
	SM = False if method=='no_softmax' else True
	if method != 'with_noise':
		test_input = [gabor(size=im_size, lambda_freq=im_size/5., theta=orientations, sigma=im_size/5., phase=0.25, noise=0.0)]
	else:
		test_input = []
		for _ in range(noise_trial):
			test_input.append(gabor(size=im_size, lambda_freq=im_size/5., theta=orientations, sigma=im_size/5., phase=0.25, noise=noise))

	curves = {}
	for r in W.keys():
		curves[r] = np.zeros((n_input, n_neurons))
		for i in range(len(test_input)):
			curves[r] += ex.propL1(test_input[i], W[r], SM=SM, t=t)/len(test_input)
		if output:
			plt.figure()
			plt.plot(curves[r])

	plt.show(block=False)

	# import pdb; pdb.set_trace()

	return curves

def preferred_orientations(W, params=None):
	"""
	compute the preferred orientation of neurons

	Args:
		W (dict): dictionary of weight matrices (each element of the dictionary is a weight matrix from an individual run)
		params (dict, optional): parameters of the main simulation (kwargs)

	returns:
		the preferred orientation of all neurons in all runs
	"""

	curves = tuning_curves(W, method='no_softmax', output=False, params=params)


	n_input = np.size(curves[curves.keys()[0]],0)

	pref_ori = {}
	for r in curves.keys():
		pref_ori[r] = np.argmax(curves[r],0) * (180./n_input) ##180??

	return pref_ori


def slopes(W, curves, pref_ori, params=None):
	"""
	compute slope of tuning curves at target orientation

	Args:
		W (dict): dictionary of weight matrices (each element of the dictionary is a weight matrix from an individual run)
		curves (dict): the tuning curves for each neuron of each run; *!!* for now does not support curves if computed with 'with_noise' method)
		pref_ori (dict): the preferred orientation of all neurons in all runs
		params (dict, optional): parameters of the main simulation (kwargs)

	returns:
		(dict): slopes of the tuning curves *!!* should be plotted so that slope value is alligned between two measurement points
	"""

	if params is not None:
		t = params['t_hid']
		target_ori = params['target_ori']

	else:
		t = 0.1
		target_ori = 70.

	n_input = np.size(curves[curves.keys()[0]],0)

	slopes = {}

	for r in W.keys():
		slopes[r] = np.abs(curves[r] - np.roll(curves[r], 1, axis=0))

		plt.figure()
		for o in np.arange(0,180,10):
			target_idx = int(o * (n_input/180))
		
			x = pref_ori[r]-o
			x[x>90]-=180
			x[x<-90]+=180
			y = slopes[r][target_idx, :]

			# plt.figure()
			plt.scatter(x, y)
			# plt.plot(curves[r][:,0])
			# plt.plot(slopes[r][:,0]*10)
		plt.show(block=False)


	# import pdb;pdb.set_trace()

	return slopes








































