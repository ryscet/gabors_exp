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

plt.close('all')
acc_cmap, norm = mpl.colors.from_levels_and_colors([0,1,2], ['red', 'blue']) 

#and then ax.scatter(x, y, c=z, cmap=cmap, norm=norm)


def plot_staircase():
    results = pd.read_csv('C:\\Users\\Ryszard\\Desktop\\gabors_exp\\stair_logs\\6.csv')
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


    
    fig, axes = plt.subplots()
    axes.plot(results['trial'], results['diff_index'], c = 'black', alpha = 0.75, linewidth = 0.5)
    #axes.plot(results['trial'], results['used_angle'], c = 'g', linestyle = '--', alpha = 0.75, linewidth = 0.5)
    
    axes.scatter(results['trial'], results['diff_index'], c= results['accuracy'], cmap=acc_cmap, norm=norm, s = 50)
    
    axes.vlines(reversals, 0,15, 'r', '--')
    #axes.plot(results['trial'], results['reversals'])
    
    axes.set_ylabel('angle magnitude in degrees')
    axes.set_xlabel('trial number')
    
    raise_window()
    
    return results
    
  
  
  
def find_latest_log():
    """Browses all logs from staircase procedure and selects the last one, i.e. the one for the current participant."""
    dir_path = os.path.dirname(os.path.realpath(__file__))


    # List all paths for logs
    paths = glob.glob(dir_path + '/stair_logs/*.csv')
    # Find the index where the log has the largets, i.e. latest, modification time (cross platform in comparison to creation time)
    last_file_idx = np.argmax(np.array([os.path.getmtime(path) for path in paths]))
    # Select the latest path
    last_file_path = paths[last_file_idx]
  
    return last_file_path 

def raise_window(figname=None):
    if figname: plt.figure(figname)
    cfm = plt.get_current_fig_manager()
    cfm.window.activateWindow()
    cfm.window.raise_()

#path = find_latest_log()
results_ = plot_staircase()
