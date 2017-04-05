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

import explore_results as explore

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


print sound.Sound

# Define the target to be detected
class instructions_params(object):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    correct_sound = sound.Sound(dir_path + '\\resources\\correct.ogg')
    incorrect_sound = sound.Sound(dir_path + '\\resources\\incorrect.ogg')
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

        instructions = ['not vertical', 'vertical']
        order = 'diff-same'
        #coin toss
        if(np.random.choice([True, False])):
            order = 'same-diff'
            instructions = list(reversed(instructions))


        self.top_response.text = instructions[0]
        self.bottom_response.text = instructions[1]

        return order

    def color_feedback(self, response):

        #self.toggle_fixation()


        if(response == 'correct'):
            self.correct_sound.play()

            self.fixation_1.lineColor = 'green'
            self.fixation_2.lineColor = 'green'
        if(response == 'wrong'):
            self.incorrect_sound.play()

            self.fixation_1.lineColor = 'red'
            self.fixation_2.lineColor = 'red'
        
        self.fixation_1.draw()
        self.fixation_2.draw()

    def reset_feedback(self):

        self.toggle_fixation()

        self.fixation_1.lineColor = 'white'
        self.fixation_2.lineColor = 'white'


    def toggle_fixation(self):
        self.fixation_1.setAutoDraw(not self.fixation_1.autoDraw)
        self.fixation_2.setAutoDraw(not self.fixation_2.autoDraw)



class trial_controller(object):
    # The gabor which appears first
    cue_triangle = visual.Polygon(win=win, edges = 3, units='norm', size=(0.4, 0.2), fillColor = 'black', lineColor = 'black', ori = 90)

    # Second gabor which is compared to the target and answered if it is the same
    probe_gabor = visual.GratingStim(win=win, mask='gauss', texRes = 2**9, units = 'deg', size = (gabor_size, gabor_size), tex = 'tri', sf = 1, interpolate = True)

    probe_orientations = []

    def __init__(self, num_trials):

         # Pseudo random shuffled list of probe angles
        self.probe_orientations = self.create_probe_angles(num_trials)



    def prepare_trial(self):
       
        # Change probe orientation by adding a value from the probe_orientations list
        t_type, angle = self.probe_orientations.pop()

        self.probe_gabor.setOri(0 + self.select_probe_angle(angle))

        return t_type, angle

 
    def select_probe_angle(self,angle):
        """ Pseudo-random shuffle from a collection of angles defined by staircase, relatively big differences and zero differences
        """
        
        # Toss a coin to choose the angle either in clockwise or counterclockwise direction
        if(np.random.choice([True, False])):
            angle = angle * -1
        
        return angle


    def create_probe_angles(self, num_trials):
        
        # Define proportion of trials for each angle value
        num_stair = int(num_trials * 0.5)
        num_big = int(num_trials * 0.05)
        num_zero = int(num_trials * 0.45)
        
        # int always rounds down, so there will usually be some trials unnasignedd. Add them to stair trials
        num_stair = num_stair + (num_trials - num_big - num_zero - num_stair )
        
        #load the staircase results
        # calculate the average of the last two levels used, this will either be the last stable success (upper bound) or include the error, i.e. lower bound
        #threshold = explore.describe_staircase(expInfo['participant']) if explore.describe_staircase(expInfo['participant']) >= 0.5 else 0.5
        threshold = 0.5
        print('threshold %.4f'%threshold)
        # Value used for the type of trials where the difference should be clearly visible
        big_angle = 45

        # Add the angle values in the amounts specified bu num trials proportions
        angle_list = [('identical', 0) for z in range(num_zero)]
        angle_list.extend([('big', np.random.normal(big_angle , scale = 2)) for b in range(num_big)])
        angle_list.extend([('threshold' , threshold) for s in range(num_stair)])

        # put the list in random order the list
        random.shuffle(angle_list)

        return list(angle_list)



