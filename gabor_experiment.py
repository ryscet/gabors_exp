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

import gabor_params as params #My own helper class

dir_path = os.path.dirname(os.path.realpath(__file__))


### LOG VARIABLES ###

responses = np.zeros(1) # Array (will get extended) keeping track of all responses.
saved_response_times = [] # used to store rt's
saved_db = OrderedDict() # Log is a dictionary, key is trial number, value is a tuple with all parameters: (thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)
pd_log = pd.DataFrame() # pandas log for online analysis

### SETUP PARAMETERS ###

num_trials = 100 # First draft of staircase length, use fixed num of trials
target_presentation_time = 2.0 # onscreen target
ISI = 5.0 # empty screen between target and probe
probe_time = 0.2 # probe onscreen time
ITI = 3.0 # between trial (from response untill new target)
response_wait = 5.0


### CONTROLLER OBJECT ###

trial_controler = params.trial_controller(num_trials) # Main helper object responsible for trial sequencing, selecting angles mainly

gui = params.instructions_params() # gui elements like written instructions, fixation cross etc

dir_path = os.path.dirname(os.path.realpath(__file__))



def main(t_control):
    
    global dir_path
    #These don't need to be global
    global responses
    global pd_log

    target = t_control.cue_triangle
    probe = t_control.probe_gabor

# TODO use psychopy logger
    for trial in range(num_trials):    
        t_type, angle =  t_control.prepare_trial() # Generates angles from shuffled list
        #### TARGET ####
        gui.toggle_fixation() # Turn fix off
        target.draw() # First cue

        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        params.win.flip()
        core.wait(target_presentation_time)
    
        ### ISI ###
        gui.toggle_fixation() # Turn fix on
        params.win.flip() #Empty screen, only fixation cross
        core.wait(ISI)
        
        #### PROBE ####
        gui.toggle_fixation() # Turn fix off
        probe.draw() # Second gabor
        
        params.win.flip()

        # Consider saving this frame to jpeg like in staircase
        # params.win.getMovieFrame() # save screen during probe to buffer 

        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        core.wait(probe_time)

        ### EMPTY ###
        params.win.flip() # small interval after probe dissapeared
        core.wait(0.2)

        gui.toggle_fixation() # Turn fix on
        params.win.flip()

        core.wait(response_wait) # Draw an empty screen for short period after probe and then show the answer instructions

        ### RESPONSE ###


        order = gui.randomize_response_instruction()


        instruction_appeared_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        

        gui.toggle_fixation() # Turn fix off

        gui.top_response.draw()
        gui.bottom_response.draw()
        gui.middle_response.draw()
        
        params.win.flip() # appear instruction

        thisResp = None
        while thisResp==None:
            
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                    
                if thisKey== 'num_4':
                    thisResp = 'up'
                    correct = check_response(thisResp, t_type, order)
                
                if thisKey == 'num_5':
                    thisResp = 'middle'
                    correct = 'dont know'

                        
                elif thisKey == 'num_6':
                    thisResp = 'down'
                    correct = check_response(thisResp, t_type, order)

        
                elif thisKey in ['escape']:
                    OnQuit()
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment

        

        # Time of keypress
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        
        # Calc response time
        response_time = (key_time - probe_appeared).total_seconds()
            
        saved_response_times.append(response_time)
        
        responses = np.append(responses, thisResp)
        
        
        saved_db[trial] = { 'trial' : trial,
                            'raw_key' : thisKey,
                            'response' : thisResp,
                            'accuracy' : correct,
                            'instruction_time' : instruction_appeared_time,
                            'order' : order, 
                            'response_time' : response_time, 
                            'trial_type' : t_type,
                            'precise_angle' : angle, 
                            'target_time' : target_appeared,
                            'probe_time' : probe_appeared,
                            'key_time' : key_time,
                            'participant' : params.expInfo['participant']}
    
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
        


        gui.color_feedback(correct)
        params.win.flip() # show color feedback, dissapear instruction

        core.wait(0.5)

        gui.reset_feedback()

        #### ITI ####
        params.win.flip() # dissapear feedback
        #params.win.saveMovieFrames('%s\\movie_frames\\%s_angle_%i_frame_%i.tif'%(dir_path, params.expInfo['participant'], stair_angle, trial))

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
