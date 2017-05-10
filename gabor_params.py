#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Gabors for variables related to psychopy
"""
import pygame 
from psychopy import prefs

from psychopy import visual, core,  monitors, gui, data #import some libraries from PsychoPy
import numpy as np
import pandas as pd
import random 
import os 
import math

#import explore_results as explore

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
        
        self.top_response = visual.TextStim(win, '', color='red', pos = (-0.5, 0.0))
        self.middle_response = visual.TextStim(win, 'don\'t know', color=[-0.5,-0.5,-0.5], pos = (0.0, 0.0))
        
        self.bottom_response = visual.TextStim(win,'', color='blue', pos = (0.5, 0.0))
     
        
# multiply by height to width ratio to get perfect square - 1080/1920
        #self.fixation_1 = visual.Line(win=win, start=(-fixation_cross_size * 0.56, 0.0), end=(fixation_cross_size * 0.56, 0.0), **{'lineColor':'white', 'lineWidth' :5.0})
        #self.fixation_2 = visual.Line(win=win, start=(0.0, -fixation_cross_size), end=(0.0,fixation_cross_size), **{'lineColor':'white', 'lineWidth' :5.0})
        
        self.fixation_1 = visual.Circle(win = win, units = 'pix', radius = 10, **{'pos' : (0,0), 'fillColor': 'white'})
        self.fixation_2 = visual.Circle(win = win, units = 'pix', radius = 4, **{'pos' : (0,0), 'fillColor': 'black'})
        

        self.fixation_1.setAutoDraw(True)
        self.fixation_2.setAutoDraw(True)
        

    def randomize_response_instruction(self):

        instructions = ['non-match', 'match']
        order = 'diff-same'
        #coin toss
        if(np.random.choice([True, False])):
            order = 'same-diff'
            instructions = list(reversed(instructions))


        self.top_response.text = instructions[0]
        self.bottom_response.text = instructions[1]

        return order



    def toggle_fixation(self):
        self.fixation_1.setAutoDraw(not self.fixation_1.autoDraw)
        self.fixation_2.setAutoDraw(not self.fixation_2.autoDraw)



class trial_controller(object):
    # The gabor which appears first
    #cue_triangle = visual.Polygon(win=win, edges = 3, units='norm', size=(0.4, 0.2), fillColor = 'black', lineColor = 'black', ori = 90)
    width = 0.025
    height = 0.040
    frame_draw = True
    frame_color = 'DarkGreen'
    # Second gabor which is compared to the target and answered if it is the same
    sample_gabor = visual.GratingStim(win=win, mask='gauss', texRes = 2**9, 
                                      units = 'deg', size = (gabor_size, gabor_size), 
                                      tex = 'sin', sf = 1, interpolate = True,
                                      depth = 1)



    left = visual.Rect(win = win, width = width, height = 1, 
                        **dict(units='norm',  fillColor=frame_color, fillColorSpace='rgb', lineColor= None,
                               pos=(-1, 0), size=2,  interpolate=False,
                               autoDraw=frame_draw))
    right = visual.Rect(win = win, width = width, height = 2, 
                        **dict(units='norm',  fillColor=frame_color, fillColorSpace='rgb', lineColor= None,
                               pos=(1, 0), size=2,  interpolate=False,
                               autoDraw=frame_draw))

    top = visual.Rect(win = win, width = 1, height = height, 
                        **dict(units='norm',  fillColor=frame_color, fillColorSpace='rgb', lineColor= None,
                               pos=(0, 1), size=2,  interpolate=False,
                               autoDraw=frame_draw))
    bottom = visual.Rect(win = win, width = 1, height = height, 
                        **dict(units='norm',  fillColor= frame_color, fillColorSpace='rgb', lineColor= None,
                               pos=(0, -1), size=2,  interpolate=False,
                               autoDraw=frame_draw))



    
    sensor_square = visual.Rect(win = win, width=0.1, height=0.15, **{'pos' : (0.8,-0.2), 'fillColor': 'white', 'units' : 'norm'})
    


    def __init__(self, num_trials):

         # Pseudo random shuffled list of probe angles
        self.match_angles = self.create_match_angles(num_trials)
        
        # List of the first gabor angles
        self.binned_angles = self.create_binned_angles(num_trials)



    def prepare_trial(self):
        # Select the angle for the first gabor, i.e. the sample
        angle_bin, first_angle = self.binned_angles.pop()
        # Set the orientation of the first gabor
        self.sample_gabor.setOri(first_angle)
        # Select the angle for the change in the second gabor, it could be 0 (match) or something (non-match)
        t_type, probe_angle = self.match_angles.pop()
        # Store the parameters in the dict to be used for logging and changing the second gabor orientation
        trial_angles = {'t_type' : t_type, 'probe_angle' : probe_angle, 'angle_bin' : angle_bin, 'first_angle' : first_angle}

        return trial_angles

    def toggle_frame(self,toggle):
        self.left.setAutoDraw(toggle)
        self.right.setAutoDraw(toggle)
        self.top.setAutoDraw(toggle)
        self.bottom.setAutoDraw(toggle)

    def set_frame_color(self, color):
        self.left.fillColor = color
        self.right.fillColor = color
        self.top.fillColor = color
        self.bottom.fillColor = color




    def create_match_angles(self, num_trials):
        # Define proportion of trials for each angle value
        num_diff= int(num_trials * 0.4) # Non match

        num_same = int(num_trials * 0.4) # Match
        
        num_control = int(num_trials * 0.2) # Control
        
        #load the staircase results
        # calculate the average of the last two levels used, this will either be the last stable success (upper bound) or include the error, i.e. lower bound
        #threshold = explore.describe_staircase(expInfo['participant']) if explore.describe_staircase(expInfo['participant']) >= 0.5 else 0.5
        #THRESHOLD
        threshold = 15.0
        
        print('threshold %.4f'%threshold)
        # Value used for the type of trials where the difference should be clearly visible

        # Add the angle values in the amounts specified bu num trials proportions
        angle_list = [('match', 0) for s in range(num_same)]
        angle_list.extend([('non-match', self.random_reflect_angle(threshold)) for d in range(num_diff)])
        angle_list.extend([('control' , None) for c in range(num_control)])
        # put the list in random order the list
        random.shuffle(angle_list)
        

        return list(angle_list)
    
    def random_reflect_angle(self, angle):
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


