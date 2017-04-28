#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Gabors for variables related to psychopy
"""
from psychopy import visual, core, monitors, gui, data #import some libraries from PsychoPy
import numpy as np
import pandas as pd
import random 
import os 
import glob
import math


# Initial window prompting for subject name
expName = u'Exp start'  # from the Builder filename that created this script
expInfo = {u'participant': u''}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

#Define the main application window
mon = monitors.Monitor('dell', width= 54.61, distance=57)
mon.setSizePix((1920, 1080))
win = visual.Window( fullscr = True, winType  ='pyglet', screen =0, waitBlanking = True, checkTiming = True, monitor = mon)
win.mouseVisible = False
gabor_size = 11
fixation_cross_size = 0.02

# Define the target to be detected
class instructions_params(object):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        
        self.top_response = visual.TextStim(win, 'match', color='blue', pos = (0.5, 0.0))
        
        self.bottom_response = visual.TextStim(win,'non-match', color='red', pos = (-0.5, - 0.0))
             
        self.fixation_1 = visual.Circle(win = win, units = 'pix', radius = 10, **{'pos' : (0,0), 'fillColor': 'white'})
        self.fixation_2 = visual.Circle(win = win, units = 'pix', radius = 4, **{'pos' : (0,0), 'fillColor': 'black'})
        

        self.fixation_1.setAutoDraw(True)
        self.fixation_2.setAutoDraw(True)
        

    def toggle_fixation(self):
        self.fixation_1.setAutoDraw(not self.fixation_1.autoDraw)
        self.fixation_2.setAutoDraw(not self.fixation_2.autoDraw)



class trial_controller(object):
    

    sample_gabor = visual.GratingStim(win=win, mask='gauss', texRes = 2**9, 
                                      units = 'deg', size = (gabor_size, gabor_size), 
                                      tex = 'sin', sf = 1, interpolate = True,
                                      depth = 1)

    # Info for staircase procedure
    last_two_responses = []
    diff_index = 0
    
    def __init__(self, num_trials):
        
        # List of the first gabor angles
        self.binned_angles = self.create_binned_angles(num_trials)
        
        # list of increasing difficulty of angles for match or non-match decision
        self.probe_orientations = np.array([45, 30, 25, 20, 18, 16, 14, 12, 10, 8, 6 , 4, 2, 1, 0])


    def decide_stair(self, response_history):
        
        angle_bin, first_angle = self.binned_angles.pop()
        # Set the orientation of the first gabor
        self.sample_gabor.setOri(first_angle)

        # Adjust the difficulty based on staircase procedure
        self.diff_index = self.adjust_diff(response_history)
        
        # Decide the new angle for the match or non-match decision
        probe_angle = self.random_reflect_angle(self.probe_orientations[self.diff_index])

        trial_angles = {'diff_index' : self.diff_index, 'probe_angle' : probe_angle, 'angle_bin' : angle_bin, 'first_angle' : first_angle}


        return trial_angles

    def adjust_diff(self,response_history):
        response_dict = {'correct': 1, 'wrong' : 0}
        
        
        response_history = [response_dict[response] for response in response_history]

        if(len(response_history) >=2): # only apply the staircase after the first two trials
        
            self.last_two_responses.append(response_history[-1])

            # decrement difficulty if there was an error. 
            if response_history[-1] == 0:
                # try to decrement it, otherwise keep at minimum
                if(self.diff_index >= 1):
                    self.diff_index = self.diff_index -1
                    print('decreasing')
                else:
                    self.diff_index = 0
                    print('already minimum difficulty')
            
            # increment difficulty after tow consecutve successess
            elif np.array(response_history[-2:]).sum() == 2 and len(self.last_two_responses) >=2:
                self.last_two_responses = []
                # Try to increment it otherwise keep at maximum
                if(self.diff_index < len(self.probe_orientations) - 1):
                    self.diff_index = self.diff_index +1
                    print('increasing')
                else:
                    self.diff_index = len(self.probe_orientations) - 1
        return self.diff_index


    def random_reflect_angle(self,angle):
        # Toss a coin to choose the angle either in clockwise or counterclockwise direction
        if(np.random.choice([True, False])):
            angle = angle * -1            
        return angle
    
    
    def create_binned_angles(self, num_trials):
        """Create angles for the first gabors from a set of binned orientations. 
        The bins are from 0 to 157.5 with step of 22.5 degrees based on Ester 2013"""
        
        bins = np.arange(0, 180, 22.5)
        
        angle_list = []
        for category_angle in bins:
            for single_angle in range(int(math.ceil(float(num_trials) / len(bins)))):
                angle = category_angle + np.random.uniform(-10,10)
                angle_list.append([category_angle, angle])
        
        random.shuffle(angle_list)
        
        return angle_list