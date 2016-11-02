#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Gabors for variables related to psychopy
"""
from psychopy import visual, core,  monitors, gui, data #import some libraries from PsychoPy

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

gabor_size = 10


# Define the stimulus to be presented
class main_stimulus(object):
    
    def __init__(self):
        

        self.grating = visual.GratingStim(win=win, mask='gauss', units = 'deg', size = (gabor_size,gabor_size), tex = 'sin', sf = 1, interpolate = True)
        

        
# Define the target to be detected
class instructions_params(object):
    
    def __init__(self):
        
        
        self.grating = visual.GratingStim(win=win, mask='gauss', units = 'deg', size = (gabor_size, gabor_size), tex = 'sin', sf = 1, interpolate = True)
        
        self.instruction_blue = visual.TextStim(win, 'different',
                       color='red', pos = (-0.75, 0.0))
        
        self.instruction_red = visual.TextStim(win,'the same',
               color='blue', pos = (0.75, 0.0))
        
        #self.instruction_red.setAutoDraw(True, log=None)
        #self.instruction_blue.setAutoDraw(True, log=None)
        
        
# multiply by height to width ratio to get perfect square - 1080/1920
        self.fixation_1 = visual.Line(win=win, start=(-0.03 * 0.56, 0.0), end=(0.03 * 0.56, 0.0), **{'lineColor':'white', 'lineWidth' :5.0})
        self.fixation_2 = visual.Line(win=win, start=(0.0, -0.03), end=(0.0, 0.03), **{'lineColor':'white', 'lineWidth' :5.0})
        #self.fixation = visual.Circle(win=win, radius = 0.1, edges =32, **{'lineColor':'red','fillColor':'red', 'units' : 'deg'})
        self.fixation_1.setAutoDraw(True, log = None)
        self.fixation_2.setAutoDraw(True, log = None)
        
        #self.circle = visual.Circle(win = win, radius=0.6, edges=256, **{'units' : 'deg', 'size' : (20,20), 'opacity' : 0.5})