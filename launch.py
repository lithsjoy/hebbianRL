import numpy as np
import support.hebbianRL as rl
import support.external as ex
import support.mnist as mnist

rl = reload(rl)
ex = reload(ex)


""" 
experimental variables

classes (int) 	: class of the MNIST dataset to use to train the network
rActions (str)	: for each class of MNIST, the action that is rewarded. Capital letters indicates a class that is paired with ACh release.
"""

# classes 	= np.array([ 0 , 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 ], dtype=int)
# rActions 	= np.array(['a','b','c','d','e','f','g','h','i','j'], dtype='|S1')

# classes 	= np.array([ 3,  4 , 5 , 7 , 8 , 9 ], dtype=int)
# rActions 	= np.array(['0','B','0','0','0','0'], dtype='|S1')
# rActions 	= np.array(['a','B','c','d','e','f'], dtype='|S1')
# rActions 	= np.array(['a','b','c','d','e','f'], dtype='|S1')

# classes 	= np.array([ 4 , 7 , 9 ], dtype=int)
# rActions 	= np.array(['a','c','a'], dtype='|S1')

classes 	= np.array([ 4 , 9 ], dtype=int)
rActions 	= np.array(['a','b'], dtype='|S1')

""" parameters """
kwargs = {
'nRun' 			: 1				,# number of runs
'nEpiCrit'		: 0				,# number of 'critical period' episodes in each run (episodes when reward is not required for learning)
'nEpiAch'		: 8				,# number of ACh episodes in each run (episodes when ACh only is active)
'nEpiProc'		: 3				,# number of 'procedural learning' episodes (to initialize the action weights after critical period)
'nEpiDopa'		: 0				,# number of 'adult' episodes in each run (episodes when reward is not required for learning)
'A' 			: 1.2			,# input normalization constant. Will be used as: (input size)*A; for images: 784*1.2=940.8
'runName' 		: 'pypet_2'		,# name of the folder where to save results
'dataset'		: 'test'		,# MNIST dataset to use; legal values: 'test', 'train' ##use train for actual results
'nHidNeurons'	: 49			,# number of hidden neurons
'lrCrit'		: 0.005 		,# learning rate during 'critica period' (pre-training, nEpiCrit)
'lrAdlt'		: 0.005			,# learning rate after the end of the 'critica period' (adult/training, nEpiAch and nEpiDopa)
'aHigh' 		: 6. 		,#<--# learning rate increase for relevance signal (high ACh) outside of critical period
'aLow'			: 1. 			,# learning rate increase without relevant signal (no ACh)
'dMid' 			: 0.6 		,#<--# learning rate increase for correct reward prediction
'dHigh' 		: 0.6*2.		,# learning rate increase for unexpected reward (high dopamine) outside of critical period
'dNeut' 		: 0.0			,# learning rate increase for no reward, when none predicted
'dLow' 			: -0.6*0.5		,# learning rate increase for incorrect reward prediction (low dopamine)
'nBatch' 		: 20 			,# mini-batch size
'classifier'	: 'neuronClass'	,# which classifier to use for performance assessment. Possible values are: 'actionNeurons', 'SVM', 'neuronClass'
'SVM'			: True			,# whether to use an SVM or the number of stimuli that activate a neuron to determine the class of the neuron
'bestAction' 	: True			,# whether to take predicted best action (True) or take random actions (False)
'feedback'		: False			,# whether to feedback activation of classification neurons to hidden neurons
'balReward'		: False			,# whether reward should sum to the same value for stim. that are always rewarded and stim. that are rewarded for specific actions
'showPlots'		: False			,# whether to display plots
'show_W_act'	: True			,# whether to display W_act weights on the weight plots
'sort' 			: False			,# whether to sort weights by their class when displaying
'target'		: 4 			,# target digit (to be used to color plots). Use None if not desired
'seed' 			: 992#np.random.randint(1000) 				# seed of the random number generator
}

kwargs['classes'] 	= classes
kwargs['rActions'] 	= rActions


""" load and pre-process images """
ex.checkClassifier(kwargs['classifier'])
kwargs['runName'] = ex.checkdir(kwargs['runName'], OW_bool=True)
print 'seed: ' + str(kwargs['seed']) + '\n'
print 'loading data...'
imPath = '/Users/raphaelholca/Documents/data-sets/MNIST'

images, labels = mnist.read_images_from_mnist(classes = kwargs['classes'], dataset = kwargs['dataset'], path = imPath)
images, labels = ex.evenLabels(images, labels, classes)

# if True: #duplicates some of the training examples, to be used instead to ach
# 	labels_ori = np.copy(labels)
# 	images_ori = np.copy(images)
# 	for i in range(3):	#number of times to duplicate the training examples
# 		for d in [4]: #digit classes to duplicate
# 			images = np.append(images, images_ori[labels_ori==d])
# 			images = np.reshape(images, (-1, 784))
# 			labels = np.append(labels, labels_ori[labels_ori==d])

allCMs, allPerf = rl.RLnetwork(images=images, labels=labels, kwargs=kwargs, **kwargs)






