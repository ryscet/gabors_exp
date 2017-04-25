#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment:
    Show a series of gabor patches pairs. First gabor is the target, sceond is the probe. Subjects reply whether the probe is identical to the target. 
    
    classmethod datetime.now([tz])
        Return the current local date and time. If optional argument tz is None or not specified, this is like today(), 
        but, if possible, supplies more precision than can be gotten from going through a time.time() timestamp 
        (for example, this may be possible on platforms supplying the C gettimeofday() function). - think this is only for unix
    
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

import gabor_params as params #My own helper class
import time 


dir_path = os.path.dirname(os.path.realpath(__file__))



### LOG VARIABLES ###

responses = np.zeros(1) # Array (will get extended) keeping track of all responses.
#saved_response_times = [] # used to store rt's
saved_db = OrderedDict() # Log is a dictionary, key is trial number, value is a tuple with all parameters: (thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)
pd_log = pd.DataFrame() # pandas log for online analysis

### SETUP PARAMETERS ###
refresh_rate = 60 # screen refresh rate in Hz. Compare it against check results returned by check.py

num_trials = 10 # First draft of staircase length, use fixed num of trials
sample_presentation_time = 1.0 # onscreen target
ISI = 5.0 # empty screen between target and probe
probe_time = 0.2 # probe onscreen time
ITI = 3.0 # between trial (from response untill new target)
response_wait = 5.0


### CONTROLLER OBJECT ###

trial_controler = params.trial_controller(num_trials) # Main helper object responsible for trial sequencing, selecting angles mainly

gui = params.instructions_params() # gui elements like written instructions, fixation cross etc

dir_path = os.path.dirname(os.path.realpath(__file__))




def main(t_control):
    # Initialize timestamps
    START_TIME = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    clock = core.MonotonicClock()

    global dir_path
    #These don't need to be global
    global responses
    global pd_log

    sample = t_control.sample_gabor

    for trial in range(num_trials):    
        t_type, angle =  t_control.prepare_trial() # Generates angles from shuffled list
        
        # COLOR FRAME for trial type, hold (DMTS) or drop (control)
        t_control.frame.autoDraw = True
        if(t_type == 'control'):
            t_control.frame.lineColor = 'DarkRed'
        else:
            t_control.frame.lineColor = 'DarkGreen'
        
        
        #### ITI ####
        ITI_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        ITI_time_psychopy = clock.getTime()

        for frame in range(int(ITI * refresh_rate)):
            params.win.flip()
        

        #### TARGET ####
        gui.toggle_fixation() # Turn fix off
        
        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        target_appeared_psychopy = clock.getTime()
        
        for frame in range(int(sample_presentation_time * refresh_rate)):
            sample.draw() # First cue
            t_control.sensor_square.draw()
            params.win.flip()
            
    
        ### ISI ###
        t_control.frame.autoDraw = False # Hide the frame informing about trial type
        gui.toggle_fixation() # Turn fix on
        for frame in range(int(ISI * refresh_rate)):
            params.win.flip() #Empty screen, only fixation cross
        
        if t_type == 'control': 
            print('not passing')
            continue
        print('passing')
        #### PROBE ####
        gui.toggle_fixation() # Turn fix off
        sample.setOri(sample.ori + angle)
        
        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        probe_appeared_psychopy = clock.getTime()
        
        for frame in range(int(probe_time * refresh_rate)):
            sample.draw() # Second gabor
            t_control.sensor_square.draw()
            params.win.flip()


        ### EMPTY ###
        for frame in range(12):
            params.win.flip() # small interval after probe dissapeared

        gui.toggle_fixation() # Turn fix on
        
        for frame in range(int(response_wait * refresh_rate)):
            params.win.flip() # Draw an empty screen for short period after probe and then show the answer instructions


        ### RESPONSE ###

        order = gui.randomize_response_instruction()

        instruction_appeared_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        instruction_appeared_time_psychopy = clock.getTime()
        gui.toggle_fixation() # Turn fix off
        
        thisResp = None
        while thisResp==None:
            gui.top_response.draw()
            gui.bottom_response.draw()
            gui.middle_response.draw()
            params.win.flip() # appear instruction

            allKeys=event.waitKeys()
            for thisKey in allKeys:
                    
                if thisKey== 'num_4':
                    thisResp = 'left'
                    correct = check_response(thisResp, t_type, order)
                
                if thisKey == 'num_5':
                    thisResp = 'middle'
                    correct = 'dont know'

                        
                elif thisKey == 'num_6':
                    thisResp = 'right'
                    correct = check_response(thisResp, t_type, order)

        
                elif thisKey in ['escape']:
                    OnQuit()
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment        

        # Time of keypress
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        key_time_psychopy = clock.getTime()
        # Calc response time
       # response_time = (key_time - probe_appeared).total_seconds()           
      # saved_response_times.append(response_time)
        
        responses = np.append(responses, thisResp)
        
        
        saved_db[trial] = { 'trial' : trial,
                            'raw_key' : thisKey,
                            'response' : thisResp,
                            'accuracy' : correct,
                            'ITI_time' : ITI_time,
                            'ITI_time_psychopy' : ITI_time_psychopy,
                            'instruction_time' : instruction_appeared_time,
                            'instruction_time_psychopy' : instruction_appeared_time_psychopy,
                            'order' : order, 
                            #'response_time' : response_time, 
                            'trial_type' : t_type,
                            'precise_angle' : angle, 
                            'target_time' : target_appeared,
                            'target_time_psychopy' : target_appeared_psychopy,
                            'probe_time' : probe_appeared,
                            'probe_time_psychopy' : probe_appeared_psychopy,
                            'key_time' : key_time,
                            'key_time_psychopy' : key_time_psychopy,
                            'participant' : params.expInfo['participant']}
    
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
        

        gui.toggle_fixation() # Turn fix off


    
    params.win.close()
    
    # Saves the logs   
    OnQuit()
    
    core.quit()

def check_response(response, trial_type, order):

    order_dict = {'diff-same' : {'left' : 'non-match',
                                 'right' : 'match' },
                  'same-diff' : {'left' : 'match',
                                 'right' : 'non-match' }
                }

    same_correct = {'match' : 'correct', 'non-match' : 'wrong'}
    diff_correct = {'match' : 'wrong', 'non-match' : 'correct'}

    trial_dict = {'non-match' : diff_correct, 
                    'control' : None,
                    'match' : same_correct
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
