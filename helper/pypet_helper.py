import os
import numpy as np
import matplotlib.pyplot as plt
import hebbian_net
import pypet
import pickle
import time


def launch_exploration(traj, images_dict, labels_dict, images_params, save_path):
	""" launch all the exploration of the parameters """
	parameter_dict = traj.parameters.f_to_dict(short_names=True, fast_access=True)
	try:
		test_perf = launch_one_exploration(parameter_dict, images_dict, labels_dict, images_params, save_path)
	except ValueError:
		test_perf = [-1.]	

	traj.f_add_result('test_perf', perf=test_perf)

def launch_one_exploration(parameter_dict, images_dict, labels_dict, images_params, save_path):
	""" launch one instance of the network """
	net = hebbian_net.Network(**parameter_dict)

	net.train(images_dict, labels_dict, images_params)

	perf_dict = net.test(images_dict, labels_dict)

	p_file = open(os.path.join(save_path, 'networks', net.name), 'w')
	pickle.dump(net, p_file)
	p_file.close()

	return perf_dict['perf_all']

def add_parameters(traj, parameter_dict):
	for k in parameter_dict.keys():
		traj.f_add_parameter(k, parameter_dict[k])

def set_run_names(explore_dict, name):
	nXplr = len(explore_dict[explore_dict.keys()[0]])
	runName_list = [name for _ in range(nXplr)]
	for n in range(nXplr):
		for k in explore_dict.keys():
			runName_list[n] += '_'
			runName_list[n] += k
			runName_list[n] += str(explore_dict[k][n]).replace('.', ',')
	return runName_list

def print_params(parameter_dict, explore_dict, save_path):
	tab_length = 25
	param_file = open(os.path.join(save_path, 'params.txt'), 'w')

	if os.path.exists(os.path.join(save_path)):
		shutil.rmtree(save_path)
		os.mkdir(save_path)
		os.mkdir(os.path.join(save_path, 'networks'))
	
	time_str = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	time_line = ('created on\t: %s\n\n' % time_str).expandtabs(tab_length)
	param_file.write(time_line)

	print_dict = parameter_dict.copy()
	print_dict.update(explore_dict)

	for p in print_dict.keys():
		if isinstance(print_dict[p], dict):
			for ik, k in enumerate(print_dict[p].keys()):
				if ik==0:
					line = ('%s \t: %s: %s\n' % (p, k, str(print_dict[p][k]))).expandtabs(tab_length)
				else:
					line = ('\t  %s: %s\n' % (k, str(print_dict[p][k]))).expandtabs(tab_length)
				param_file.write(line)
		else:
			line = ('%s \t: %s\n' %( p, str(print_dict[p]) )).expandtabs(tab_length)
			param_file.write(line)
	param_file.close()

def plot_results(folder_path=''):
	if folder_path=='':
		folder_path = '/Users/raphaelholca/Dropbox/hebbian_net/output/test_pypet_0/'
		# folder_path = '/Users/raphaelholca/Mountpoint/hebbianRL/output/proba_two_lin/'

	traj_name = 'explore_perf'
	traj = pypet.load_trajectory(traj_name, filename=os.path.join(folder_path, 'explore_perf.hdf5'), force=True)
	traj.v_auto_load = True

	perf_all = []
	for run in traj.f_iter_runs():
		perf_all.append(traj.results[run].test_perf['perf'])
	perf_all = np.array(perf_all)
	perf = np.mean(perf_all,1)

	param_traj = traj.f_get_explored_parameters()
	param = {}
	for k in param_traj:
		if k[11:] != 'name':
			xplr_values = np.array(param_traj[k].f_get_range())
			if len(np.unique(xplr_values)) >1:
				param[k[11:]] = xplr_values

	arg_best = np.argmax(perf)

	best_param = {}

	print 'best parameters:'
	print '================'
	for k in param.keys():
		best_param[k] = param[k][arg_best]
		print k + ' : ' + str(param[k][arg_best]) + '\t\t' + str(np.round(np.unique(param[k]),3))
	print "\nbest performance: " + str(np.round(np.max(perf)*100,2)) + "\n"

	keys = param.keys()
	for ik in range(len(keys)):
		if len(keys)==1: ik=-1
		for k in keys[ik+1:]:
			others = keys[:]
			if len(keys)>1: 
				others.remove(keys[ik])
				others.remove(k)
			
			mask = np.ones_like(param[k], dtype=bool)
			if len(param)>2:
				for o in others:
					mask = np.logical_and(mask, param[o]==best_param[o])
			pX = param[keys[ik]][mask]
			pY = param[k][mask]
			rC = np.hstack(perf)[mask]

			if True: #True: non-linear representation of results; False: linear representation 
				ipX = np.zeros(len(pX))
				ipY = np.zeros(len(pY))
				for i in range(len(pX)):
					ipX[i] = np.argwhere(pX[i]==np.sort(np.unique(pX)))
					ipY[i] = np.argwhere(pY[i]==np.sort(np.unique(pY)))
			else:
				ipX = np.copy(pX)
				ipY = np.copy(pY)

			fig = plt.figure()
			fig.patch.set_facecolor('white')
			
			plt.scatter(ipX, ipY, c=rC, cmap='CMRmap', vmin=np.min(perf)-0.1, vmax=np.max(perf), s=1000, marker='s')
			# plt.scatter(param[keys[ik]][arg_best], param[k][arg_best], c='r', s=50, marker='x')
			for i in range(len(pX)):
				if pX[i]==param[keys[ik]][arg_best] and pY[i]==param[k][arg_best]:
					plt.text(ipX[i], ipY[i], str(np.round(rC[i]*100,1)), horizontalalignment='center', verticalalignment='center', weight='bold', bbox=dict(facecolor='red', alpha=0.5))
				else:
					plt.text(ipX[i], ipY[i], str(np.round(rC[i]*100,1)), horizontalalignment='center', verticalalignment='center')
			plt.xticks(ipX, pX)
			plt.yticks(ipY, pY)
			plt.xlabel(keys[ik], fontsize=25)
			plt.ylabel(k, fontsize=25)
			plt.tick_params(axis='both', which='major', labelsize=18)
			plt.tight_layout()
			plt.savefig(os.path.join(folder_path, keys[ik] + '_' + k + '.pdf'))

	plt.close(fig)
