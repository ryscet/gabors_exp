#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Gabors for variables related to psychopy
"""
import pygame 
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, core,  monitors, gui, data, sound #import some libraries from PsychoPy
import numpy as np
import pandas as pd
import random 
import os 
import glob

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
gabor_size = 10
fixation_cross_size = 0.02


NUM_CONTROL = 30  # Number of control, or 'drop trials'

# Define the target to be detected
class instructions_params(object):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    correct_sound = sound.Sound(dir_path + '/resources/correct.ogg')
    incorrect_sound = sound.Sound(dir_path + '/resources/incorrect.ogg')
    print(dir_path)

    def __init__(self):
        
        self.top_response = visual.TextStim(win, '', color='red', pos = (-0.5, 0.0))
        self.middle_response = visual.TextStim(win, 'don\'t know', color=[-0.5,-0.5,-0.5], pos = (0.0, 0.0))
        
        self.bottom_response = visual.TextStim(win,'', color='blue', pos = (0.5, 0.0))
     
        
# multiply by height to width ratio to get perfect square - 1080/1920
        self.fixation_1 = visual.Line(win=win, start=(-fixation_cross_size * 0.56, 0.0), end=(fixation_cross_size * 0.56, 0.0), **{'lineColor':'white', 'lineWidth' :5.0})
        self.fixation_2 = visual.Line(win=win, start=(0.0, -fixation_cross_size), end=(0.0,fixation_cross_size), **{'lineColor':'white', 'lineWidth' :5.0})

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

#    def color_feedback(self, response):
#
#        #self.toggle_fixation()
#
#
#        if(response == 'correct'):
#            self.correct_sound.play()
#
#            self.fixation_1.lineColor = 'green'
#            self.fixation_2.lineColor = 'green'
#        if(response == 'wrong'):
#            self.incorrect_sound.play()
#
#            self.fixation_1.lineColor = 'red'
#            self.fixation_2.lineColor = 'red'
#        
#        self.toggle_fixation()


#    def reset_feedback(self):
#
#        self.toggle_fixation()
#
#        self.fixation_1.lineColor = 'white'
#        self.fixation_2.lineColor = 'white'


    def toggle_fixation(self):
        self.fixation_1.setAutoDraw(not self.fixation_1.autoDraw)
        self.fixation_2.setAutoDraw(not self.fixation_2.autoDraw)



class trial_controller(object):
    # The gabor which appears first
    #cue_triangle = visual.Polygon(win=win, edges = 3, units='norm', size=(0.4, 0.2), fillColor = 'black', lineColor = 'black', ori = 90)

    # Second gabor which is compared to the target and answered if it is the same
    sample_gabor = visual.GratingStim(win=win, mask='gauss', texRes = 2**9, units = 'deg', size = (gabor_size, gabor_size), tex = 'tri', sf = 1, interpolate = True)

    frame = visual.ShapeStim(win = win, units='norm', lineWidth=50, lineColor='green', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', 
                             vertices=[ [-1.0, -1.0] , [-1.0, 1.0] , [1.0,1.0] , [1.0,-1.0] ], closeShape=True,
                             pos=(0, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, 
                             name=None, autoLog=None, autoDraw=True)
    
    sensor_square = visual.Rect(win = win, width=0.4, height=0.4, **{'pos' : (1,-1), 'fillColor': 'white'})


    match_angles = []

    def __init__(self, num_trials):

         # Pseudo random shuffled list of probe angles
        self.match_angles = self.create_sample_angles(num_trials)



    def prepare_trial(self):
       
        # Change probe orientation by adding a value from the probe_orientations list
        t_type, angle = self.match_angles.pop()

        self.sample_gabor.setOri(np.random.normal(0, 360))

        return t_type, angle

 
    def select_sample_angle(self,angle):
        """ Pseudo-random shuffle from a collection of angles defined by staircase, relatively big differences and zero differences
        """
        
        # Toss a coin to choose the angle either in clockwise or counterclockwise direction
        if(np.random.choice([True, False])):
            angle = angle * -1
        
        return angle


    def create_sample_angles(self, num_trials):
        global NUM_CONTROL
        # Define proportion of trials for each angle value
        num_diff= int(num_trials * 0.5)
        #num_big = int(num_trials * 0.05)
        num_same = int(num_trials * 0.5)
        
        num_control = NUM_CONTROL
        
        #load the staircase results
        # calculate the average of the last two levels used, this will either be the last stable success (upper bound) or include the error, i.e. lower bound
        #threshold = explore.describe_staircase(expInfo['participant']) if explore.describe_staircase(expInfo['participant']) >= 0.5 else 0.5
        threshold = 5.0
        print('threshold %.4f'%threshold)
        # Value used for the type of trials where the difference should be clearly visible

        # Add the angle values in the amounts specified bu num trials proportions
        angle_list = [('match', 0) for s in range(num_same)]
        angle_list.extend([('non-match' , threshold) for d in range(num_diff)])
        angle_list.extend([('control' , None) for c in range(num_control)])
        # put the list in random order the list
        random.shuffle(angle_list)

        return list(angle_list)



