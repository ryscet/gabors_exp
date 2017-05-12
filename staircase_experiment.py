#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment:
    Show a series of gabor patches pairs. First gabor is the target, sceond is the probe. Subjects reply whether the probe is identical to the target. 
    
"""
from psychopy import prefs

import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict
import pickle 
import os 

from psychopy import event, core

import staircase_params as params #My own helper class

refresh_rate = 60 # screen refresh rate in Hz. Compare it against check results returned by check.py

# TIMINGS
# Stimulus timings from Serences 2009
sample_presentation_time = 1.0 # onscreen target 
ISI = 5.0 # empty screen between target and probe
probe_time = 1.0 # probe onscreen time
ITI = 3.0 # between trial (from response untill new target)
response_wait = 2.0
### SETUP PARAMETERS ###
num_trials = 40 # First draft of staircase length, use fixed num of trials

def main():
    
    # Initialize timestamps
    START_TIME = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    clock = core.MonotonicClock()
    
    ### STAIRCASE ###
    accuracy = [] # List of strings: 'correct' or 'wrong'


    ### LOG VARIABLES ###
    saved_db = OrderedDict() # Log is a dictionary, key is trial number, value is a tuple with all parameters: (thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)
    pd_log = pd.DataFrame() # pandas log for online analysis




    ### CONTROLLER OBJECT ###
    t_control = params.trial_controller(num_trials) # Main helper object responsible for trial sequencing, selecting angles mainly
    gui = params.instructions_params() # gui elements like written instructions, fixation cross etc

    dir_path = os.path.dirname(os.path.realpath(__file__))

    sample_gabor = t_control.sample_gabor

    for trial in range(num_trials):
        
        trial_angles = t_control.decide_stair(accuracy)

        diff_index, probe_angle, angle_bin, first_angle = trial_angles['diff_index'], trial_angles['probe_angle'], trial_angles['angle_bin'], trial_angles['first_angle']
        
        print('angle: %.4f diff index: %i'%(probe_angle, diff_index))        
        
        
        #### ITI ####
        ITI_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        ITI_time_psychopy = clock.getTime()

        for frame in range(int(ITI * refresh_rate)):
            params.win.flip()
        
        #### TARGET ####
        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        target_appeared_psychopy = clock.getTime()
                
        for frame in range(int(sample_presentation_time * refresh_rate)):
            
            if(frame % phase_frames == 0):
                print(frame)
                sample.setPhase(phase_step, '+')

            sample_gabor.draw() # First cue # First cue, OREINTAION SET IN gabor_params in prepare_trial()
            params.win.flip()
    
        ### ISI ###
        ISI_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        ISI_time_psychopy = clock.getTime()
        
        for frame in range(int(ISI * refresh_rate)):
            params.win.flip() #Empty screen, only fixation cross
        
        
        #### PROBE ####
        sample_gabor.setOri(sample_gabor.ori + probe_angle) # Change the orientation according to staircase
        
        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        probe_appeared_psychopy = clock.getTime()
        
        for frame in range(int(probe_time * refresh_rate)):

            if(frame % phase_frames == 0):
                print(frame)
                sample.setPhase(phase_step, '+')

            sample_gabor.draw() # Second gabor
            params.win.flip()


        ### EMPTY ###
        
        for frame in range(int(response_wait * refresh_rate)):
            params.win.flip() # Draw an empty screen for short period after probe and then show the anwsers's instructions


        instruction_appeared_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        instruction_appeared_time_psychopy = clock.getTime()
    
        thisResp = None
        while thisResp==None:
       
            gui.top_response.draw()
            gui.bottom_response.draw() 
            params.win.flip()
            
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                print(thisKey)
                if thisKey=='num_4':
                    thisResp = 'correct'
                        
                elif thisKey == 'num_6':
                    thisResp = 'wrong'

                elif thisKey in ['escape']:
                    OnQuit(dir_path, pd_log, saved_db) # Actual call to save the data
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment


        # Time of keypress
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        
            
        
        accuracy.append(thisResp)
        

        saved_db[trial] = { 'trial' : trial,
                            'angle_bin' : angle_bin,
                            'first_angle' : first_angle,
                            'response' : thisKey,
                            'accuracy' : thisResp,
                            'diff_index' : diff_index,
                            'precise_angle' : probe_angle, 
                            'target_time' : target_appeared,
                            'target_time_psychopy' : target_appeared_psychopy,
                            'key_time' : key_time,
                            'instruction_appeared_time' : instruction_appeared_time,
                            'instruction_appeared_time_psychopy' : instruction_appeared_time_psychopy,
                            'probe_appeared' : probe_appeared,
                            'probe_appeared_psychopy' : probe_appeared_psychopy,
                            'ISI_time' : ISI_time,
                            'ISI_time_psychopy' : ISI_time_psychopy,
                            'ITI_time' : ITI_time,
                            'ITI_time_psychopy' : ITI_time_psychopy,
                            'participant' : params.expInfo['participant'],
                            'START_TIME' : START_TIME}
    
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
    
    
    
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
