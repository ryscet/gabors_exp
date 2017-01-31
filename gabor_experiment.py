#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment:
    Show a series of gabor patches pairs. First gabor is the target, sceond is the probe. Subjects reply whether the probe is identical to the target. 
    
"""
import pygame 
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']

from psychopy import sound 

import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict
import pickle 
import os 

from psychopy import event, core

import exp_params as params #My own helper class

dir_path = os.path.dirname(os.path.realpath(__file__))


### LOG VARIABLES ###

responses = np.zeros(1) # Array (will get extended) keeping track of all responses.
saved_response_times = [] # used to store rt's
saved_db = OrderedDict() # Log is a dictionary, key is trial number, value is a tuple with all parameters: (thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)
pd_log = pd.DataFrame() # pandas log for online analysis

### SETUP PARAMETERS ###

num_trials = 40 # First draft of staircase length, use fixed num of trials
target_presentation_time = 2.0 # onscreen target
ISI = 4.0 # empty screen between target and probe
probe_time = 0.2 # probe onscreen time
ITI = 3.0 # between trial (from response untill new target)
response_wait = 4.0


### CONTROLLER OBJECT ###

trial_controler = params.trial_controller(num_trials) # Main helper object responsible for trial sequencing, selecting angles mainly

gui = params.instructions_params() # gui elements like written instructions, fixation cross etc

dir_path = os.path.dirname(os.path.realpath(__file__))

correct_sound = sound.Sound(dir_path + '\sounds\correct.ogg')
incorrect_sound = sound.Sound(dir_path + '\sounds\incorrect.ogg')
print(dir_path)

def main(t_control):
    
    global dir_path
    #These don't need to be global
    global responses
    global last_two_responses
    global pd_log

    target = t_control.target_gabor
    probe = t_control.probe_gabor

# TODO use psychopy logger
    for trial in range(num_trials):    
        t_type, angle, target_ori =  t_control.prepare_trial() # Generates angles from shuffled list
        #### TARGET ####
        target.draw() # First gabor

        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        params.win.flip()
        core.wait(target_presentation_time)
    
        ### ISI ###
        params.win.flip() #Empty screen, only fixation cross
        core.wait(ISI)
        
        #### PROBE ####
        
        probe.draw() # Second gabor
        
        params.win.flip()
        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        core.wait(probe_time)

        ### EMPTY ###
        params.win.flip()

        core.wait(response_wait)

        ### RESPONSE ###

        # Draw an empty screen for short period after probe and then show the answer instructions
        order = gui.randomize_response_instruction()
        gui.top_response.draw()
        gui.bottom_response.draw()
        
        params.win.flip()
            
        thisResp = None
        while thisResp==None:
            
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                    
                if thisKey=='a':
                    thisResp = 'up'
                    correct = check_response(thisResp, t_type, order)
                        
                elif thisKey == 'l':
                    thisResp = 'down'
                    correct = check_response(thisResp, t_type, order)

        
                elif thisKey in ['escape']:
                    OnQuit()
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment
        gui.color_feedback(correct)

        params.win.flip()



        # Time of keypress
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        
        # Calc response time
        response_time = (key_time - probe_appeared).total_seconds()
            
        saved_response_times.append(response_time)
        
        responses = np.append(responses, thisResp)
        
        
        saved_db[trial] = { 'trial' : trial,
                            'response' : thisResp,
                            'order' : order, 
                            'response_time' : response_time, 
                            'trial_type' : t_type,
                            'precise_angle' : angle, 
                            'target_orientaion' : target_ori,
                            'target_time' : target_appeared,
                            'probe_time' : probe_appeared,
                            'key_time' : key_time,
                            'participant' : params.expInfo['participant']}
    
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
        

        core.wait(1.0) 
        gui.reset_feedback()

        params.win.flip()

        #params.win.getMovieFrame(buffer = 'back')   # Defaults to front buffer, I.e. what's on screen now.
        
        #params.win.saveMovieFrames(dir_path + '\\bckp_recordings\\' + expInfo['participant'] + '_bckp.mp4')

    
        #### ITI ####
        core.wait(ITI)
    
    
    params.win.close()
    
    # Saves the logs   
    OnQuit()
    
    core.quit()

def check_response(response, trial_type, order):

    order_dict = {'diff-same' : {'up' : 'different',
                                 'down' : 'same' },
                  'same-diff' : {'up' : 'same',
                                 'down' : 'different' }
                }

    same_correct = {'same' : 'correct', 'different' : 'wrong'}
    diff_correct = {'same' : 'wrong', 'different' : 'correct'}

    trial_dict = {'threshold' : diff_correct, 
                    'big' : diff_correct,
                    'identical' : same_correct
                }

    response = trial_dict[trial_type][order_dict[order][response]]
    print(response)
    

    return response

def OnQuit():
    """Called at the end of script and saves logs to disk"""    
    
    pd_log.to_csv(dir_path +'/exp_logs/'+ params.expInfo['participant'] + '.csv', index_label = 'index_copy')
    with open(dir_path + '/exp_logs/' + params.expInfo['participant'] + datetime.now().strftime('_%Y_%m_%d_') + 'log.pickle', 'wb') as handle:
        pickle.dump(saved_db, handle)
    
        
    
    
if __name__ == '__main__':
    main(trial_controler)
