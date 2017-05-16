#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 13:25:01 2016

@author: user
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import pandas as pd
import os
import glob
from scipy import misc
import itertools
list(itertools.combinations(range(6), 2))


plt.style.use('ggplot')
plt.close('all')
acc_cmap, norm = mpl.colors.from_levels_and_colors([0,1,2], ['red', 'blue'])



def inspect_images():
    
    path = 'C:/Users/Ryszard/Desktop/vertical/movie_frames/'
    all_angles = glob.glob(path + '*')
    o_angles = [misc.imread(fname).astype(float)[:, :, 0] for fname in all_angles if 'angle_1' in fname]
    i_angles = [misc.imread(fname).astype(float)[:, :, 0] for fname in all_angles if 'angle_1' in fname]
    
    assert len(o_angles) == len(i_angles)
    #test_same_angle(o_angles)
    #test_same_angle(i_angles)
    
    test_different_angles(o_angles, i_angles)
    

def test_same_angle(frames):
    combinations = list(itertools.combinations(range(len(frames)), 2))
    
    for comb in combinations:
        diff = frames[comb[0]] - frames[comb[1]]
        if(diff.max() != 0):
            print('HOUSTON WE HAVE A PROBLEM')
        
def test_different_angles(a, b):
    combinations = list(itertools.product(a, b))
    

    for c in combinations:
        diff = c[0] - c[1]
        if(diff.max() == 0):
            print('HOUSTON WE HAVE A PROBLEM')

        
        
        
def describe_staircase(subject_name, plot = False):
    #results = pd.read_csv(find_latest_log(subject_name))
    results = pd.read_csv('D:/Users/rcetnarski/Desktop/gabors_exp/stair_logs/kasiaj2.csv.csv')
    results.replace({'accuracy': {'correct' :1, 'wrong' : 0}}, inplace = True)
    
    slopes = np.insert(np.diff(results['diff_index'].as_matrix(),1),0,0)
    non_zero_indexes = np.nonzero(slopes)[0]

    #zero_crossings = np.where(np.diff(np.sign(results['reversals'])))[0]

    zero_crossings = np.where(np.diff(np.sign(slopes[non_zero_indexes])))[0]
    
    reversals= []
    for crossing in zero_crossings:
        
        if slopes[non_zero_indexes[crossing] + 1] == 0:
            #print('GOTCHA: %i'%crossing)    
            reversals.append(non_zero_indexes[crossing] +1)
        else:
            reversals.append(non_zero_indexes[crossing])

    reversal_levels = results['diff_index'].iloc[reversals]

    threshold_angle = results['precise_angle'].iloc[reversals].mean()
    
    if plot:
        fig, axes = plt.subplots()
        
        fig.suptitle('Staircase results: %.4f'%threshold_angle, fontweight = 'bold' )
        
        axes.plot(results['trial'], results['diff_index'], c = 'black', alpha = 0.75, linewidth = 0.5, label = '')
        #axes.plot(results['trial'], results['used_angle'], c = 'g', linestyle = '--', alpha = 0.75, linewidth = 0.5)
        
        axes.scatter(results['trial'], results['diff_index'], c= results['accuracy'], cmap=acc_cmap, norm=norm, s = 50, label = 'accuracy')
        
        axes.scatter(reversals,results['diff_index'].iloc[reversals],  s=100, facecolors='none', edgecolors='r', label = 'reversals')
        #axes.plot(results['trial'], results['reversals'])
        axes.axhline(reversal_levels.mean(), label = 'average reversals')
        axes.set_ylabel('difficulty level')
        axes.set_xlabel('trial number')
        
        plt.legend(loc = 'best')
        
        plt.show()
        #raise_window()
        
    return threshold_angle
    
  
  
  
def find_latest_log(subject_name):
    """Browses all logs from staircase procedure and selects the last one, i.e. the one for the current participant."""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # List all paths for logs
    paths = glob.glob(dir_path + '/stair_logs/*.csv')
    # Find the index where the log has the largets, i.e. latest, modification time (cross platform in comparison to creation time)
    last_file_idx = np.argmax(np.array([os.path.getmtime(path) for path in paths]))
    # Select the latest path
    last_file_path = paths[last_file_idx]

    assert subject_name in last_file_path

  
    return last_file_path 

#def raise_window(figname=None):
#    if figname: plt.figure(figname)
#    cfm = plt.get_current_fig_manager()
#    cfm.window.activateWindow()
#    cfm.window.raise_()

#path = find_latest_log()
#results_ = plot_staircase()
#describe_staircase( 'trial_1', plot = True)