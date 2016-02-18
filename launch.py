"""
Author: Raphael Holca-Lamarre
Date: 23/10/2014

This code creates a hebbian neural network object and trains it on the MNIST dataset. The learning rule is a hebbian learning rule augmented with a learning mechanism inspired from dopamine signalling in animal cortex.
"""

import os
import matplotlib
if 'Documents' in os.getcwd(): matplotlib.use('Agg')
import numpy as np
import time
import hebbian_net
import helper.external as ex
import helper.assess_network as an

hebbian_net = reload(hebbian_net)
ex = reload(ex)
an = reload(an)

""" create Hebbian neural network """
net = hebbian_net.Network(	dHigh 			= 0.8,#2.4,#
							dMid 			= 0.01,#0.001,#
							dNeut 			= -0.1,#-0.08,#
							dLow 			= -0.4,#-0.4,#
							protocol		= 'gabor',
							name 			= 'gabor_t_noise_0-05_167',
							n_runs 			= 1,		
							n_epi_crit		= 10,				
							n_epi_dopa		= 5,				
							t				= 0.1, 							
							A 				= 1.2,
							lr				= 0.002,#0.005,#
							batch_size 		= 50,
							n_hid_neurons	= 16,#49,#
							init_file		= '',
							lim_weights		= False,
							noise_std		= 0.2,
							exploration		= True,
							pdf_method 		= 'fit',
							classifier		= 'neural',
							test_each_epi	= True,
							verbose			= True,
							seed 			= 977 #np.random.randint(1000)
							)

""" load and pre-process training and testing images """
images_dict, labels_dict, images_params = ex.load_images(	protocol 		= net.protocol,
															A 				= net.A,
															verbose 		= net.verbose,
															digit_params 	= {	'dataset_train'	: 'train',
																				# 'classes' 		: np.array([ 4, 7, 9 ], dtype=int),
																				'classes' 		: np.array([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ], dtype=int),
																				'dataset_path' 	: '/Users/raphaelholca/Documents/data-sets/MNIST',
																				'shuffle'		: False
																				},
															gabor_params 	= {	'n_train' 		: 10000,
																				'n_test' 		: 10000,
																				'target_ori' 	: 167.,
																				'excentricity' 	: 3.0,
																				'noise'			: 0.05,
																				'im_size'		: 28,
																				}
															)

tic = time.time()

net.train(images_dict, labels_dict, images_params)

toc = time.time()

perf_dict = net.test(images_dict, labels_dict)

ex.save_net(net)

an.assess(	net,
			save_data	= True, 
			show_W_act	= True, 
			sort		= None, 
			target 		= None
			)

print '\nrun name:\t' + net.name
print 'start time:\t' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(tic))
print 'end time:\t' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(toc))
print 'train time:\t' + time.strftime("%H:%M:%S", time.gmtime(toc-tic))





















