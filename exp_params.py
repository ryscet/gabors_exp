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

# Initial window prompting for subject name
expName = u'Exp start'  # from the Builder filename that created this script
expInfo = {u'participant': u''}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

#Define the main application window
mon = monitors.Monitor('dell', width= 54.61, distance=57)
mon.setSizePix([1920, 1080])
win = visual.Window( fullscr = True, winType  ='pyglet', screen =0, waitBlanking = True, checkTiming = True, monitor = mon)
win.mouseVisible = False

gabor_size = 10
fixation_cross_size = 0.02



# Define the target to be detected
class instructions_params(object):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        
        self.top_response = visual.TextStim(win, 'vertical', color='blue', pos = (0.0, 0.25))
        
        self.bottom_response = visual.TextStim(win,'not vertical', color='red', pos = (0.0, - 0.25))
     
        
        # multiply by height to width ratio to get perfect square - 1080/1920
        self.fixation_1 = visual.Line(win=win, start=(-fixation_cross_size * 0.56, 0.0), end=(fixation_cross_size * 0.56, 0.0), **{'lineColor':'white', 'lineWidth' :5.0})
        self.fixation_2 = visual.Line(win=win, start=(0.0, -fixation_cross_size), end=(0.0,fixation_cross_size), **{'lineColor':'white', 'lineWidth' :5.0})

        self.fixation_1.setAutoDraw(True)
        self.fixation_2.setAutoDraw(True)
        

    def toggle_fixation(self):
        self.fixation_1.setAutoDraw(not self.fixation_1.autoDraw)
        self.fixation_2.setAutoDraw(not self.fixation_2.autoDraw)



class trial_controller(object):
    
    # The cue which appears first
    cue_triangle = visual.Polygon(win=win, edges = 3, units='norm', size=(0.4, 0.2), fillColor = 'black', lineColor = 'black', ori = 90)

    # Gabor which judged to be vertical or not
    probe_gabor = visual.GratingStim(win=win, mask='gauss', texRes = 2**9, units = 'deg', size = (gabor_size, gabor_size), tex = 'tri', sf = 1, interpolate = True)

    probe_orientations = np.array([])

    last_two_responses = []

    diff_index = 0
    def __init__(self, num_trials):
        
         # Pseudo random shuffled list of probe angles
        self.probe_orientations = self.create_stair_angles()


    def decide_stair(self, response_history):

        self.diff_index = self.adjust_diff(response_history)

        angle = self.probe_orientations[self.diff_index]

        self.probe_gabor.setOri(0 + self.add_noise_to_angle(angle))

        return angle, self.diff_index

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

 
    def add_noise_to_angle(self,angle):
        """ Pseudo-random shuffle from a collection of angles defined by staircase, relatively big differences and zero differences
        """

        # Add small gaussian noise
        #angle = np.random.normal(angle, scale = 0.01)
        
        # Toss a coin to choose the angle either in clockwise or counterclockwise direction
        if(np.random.choice([True, False])):
            angle = angle * -1.0
        
        return angle


    def create_stair_angles(self):
        # Draws angles from a decaying exponential distribution
        steps = np.arange(0, 25, 1)

        angle_list = np.array([self.exponential_function(x) for x in steps])
        #angle_list = np.array([0 for x in steps])

        return angle_list



    def exponential_function(self, x):
        return 2.0**(-0.5*x + 4)