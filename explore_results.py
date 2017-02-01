#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 13:25:01 2016

@author: user
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

acc_cmap, norm = mpl.colors.from_levels_and_colors([0,1,2], ['red', 'blue']) 

#and then ax.scatter(x, y, c=z, cmap=cmap, norm=norm)


def plot_staircase(name):
    results = pd.read_csv('stair_logs/%s.csv' %name )
    
    fig, axes = plt.subplots()
    axes.plot(results['trial'], results['raw_angle'], c = 'black', alpha = 0.75, linewidth = 0.5)
    #axes.plot(results['trial'], results['used_angle'], c = 'g', linestyle = '--', alpha = 0.75, linewidth = 0.5)
    
    axes.scatter(results['trial'], results['raw_angle'], c= results['accuracy'], cmap=acc_cmap, norm=norm, s = 50)

    axes.set_ylabel('angle magnitude in degrees')
    axes.set_xlabel('trial number')
    
    raise_window()
    
def raise_window(figname=None):
    if figname: plt.figure(figname)
    cfm = plt.get_current_fig_manager()
    cfm.window.activateWindow()
    cfm.window.raise_()