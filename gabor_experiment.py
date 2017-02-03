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



def main():

    ### LOG VARIABLES ###
    accuracy = [] # List of strings: 'correct' or 'wrong'
    responses = np.zeros(1) # Array (will get extended) keeping track of all responses.
    saved_response_times = [] # used to store rt's
    saved_db = OrderedDict() # Log is a dictionary, key is trial number, value is a tuple with all parameters: (thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)
    pd_log = pd.DataFrame() # pandas log for online analysis

    ### SETUP PARAMETERS ###
    num_trials = 50 # First draft of staircase length, use fixed num of trials
    target_presentation_time = 2.0 # onscreen target
    ISI = 2.0 # empty screen between target and probe
    probe_time = 0.2 # probe onscreen time
    ITI = 3.0 # between trial (from response untill new target)
    response_wait = 0.5

    ### CONTROLLER OBJECT ###
    t_control = params.trial_controller(num_trials) # Main helper object responsible for trial sequencing, selecting angles mainly
    gui = params.instructions_params() # gui elements like written instructions, fixation cross etc

    dir_path = os.path.dirname(os.path.realpath(__file__))

    target = t_control.cue_triangle
    probe = t_control.probe_gabor

# TODO use psychopy logger
    for trial in range(num_trials):
        stair_angle, diff_index = t_control.decide_stair(accuracy) # Generates angles from shuffled list
        print('angle: %.4f diff index: %i'%(stair_angle, diff_index))        
        #### TARGET ####
        gui.toggle_fixation() # Turn fix off
        target.draw() # First gabor

        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')) # save target time
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

        params.win.getMovieFrame() # save screen during probe to buffer 

        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        core.wait(probe_time)

        ### EMPTY ###
        params.win.flip()
        core.wait(0.2)


        ### RESPONSE ###
        gui.toggle_fixation() # Turn fix on

        gui.top_response.draw()
        gui.bottom_response.draw()
        
        params.win.flip()
    
        thisResp = None
        while thisResp==None:
            
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                    
                if thisKey=='a':
                    thisResp = 'correct'
                        
                elif thisKey == 'l':
                    thisResp = 'wrong'

                elif thisKey in ['escape']:
                    OnQuit(dir_path, pd_log, saved_db) # Actual call to save the data
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment


        # Time of keypress
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        
        # Calc response time
        response_time = (key_time - probe_appeared).total_seconds()
            
        saved_response_times.append(response_time)
        
        raw_responses = np.append(responses, thisKey)
        accuracy.append(thisResp)
        
        saved_db[trial] = { 'trial' : trial,
                            'response' : thisKey,
                            'accuracy' : thisResp,
                            'response_time' : response_time, 
                            'diff_index' : diff_index,
                            'precise_angle' : stair_angle, 
                            'target_time' : target_appeared,
                            'probe_time' : probe_appeared,
                            'key_time' : key_time,
                            'participant' : params.expInfo['participant']}
    
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
    
        #### ITI ####
        params.win.flip() # Clear the screen after the trial
        params.win.saveMovieFrames('%s\\movie_frames\\%s_angle_%i_frame_%i.tif'%(dir_path, params.expInfo['participant'], stair_angle, trial))

        #win.params.saveMovieFrames('frame.tif')
        core.wait(ITI)
    
    
    params.win.close()
    
    # Saves the logs   
    OnQuit(dir_path, pd_log, saved_db)
    
    core.quit()



def OnQuit(dir_path, pd_log, saved_db):
    """Called at the end of script and saves logs to disk"""    
    
    pd_log.to_csv(dir_path +'/stair_logs/'+ params.expInfo['participant'] + '.csv', index_label = 'index_copy')
    with open(dir_path + '/stair_logs/' + params.expInfo['participant'] + datetime.now().strftime('_%Y_%m_%d_') + 'log.pickle', 'wb') as handle:
        pickle.dump(saved_db, handle)
    
        
    
    
if __name__ == '__main__':
    main()
