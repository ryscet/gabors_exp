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
from psychopy import prefs

import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict
import pickle 
import os 
import random
from psychopy import event, core

import gabor_params as params #My own helper class

LIGHT_SENSOR = False # Whether to display the white square to mark stimulus onscreen with a light sensor

### SETUP PARAMETERS ###
refresh_rate = 60 # screen refresh rate in Hz. Compare it against check results returned by check.py

num_trials = 80 # First draft of staircase length, use fixed num of trials
# Stimulus timings from Serences 2009
sample_presentation_time = 1.0 # onscreen target 
ISI = 5.0 # empty screen between target and probe
probe_time = 1.0 # probe onscreen time
ITI = 3.0 # between trial (from response untill new target)
ITI_2 = 3.0

response_wait = 1.0

phase_step = 0.5 
phase_frames = 20

### CONTROLLER OBJECT ###

trial_controler = params.trial_controller(num_trials) # Main helper object responsible for trial sequencing, selecting angles mainly

gui = params.instructions_params() # gui elements like written instructions, fixation cross etc

dir_path = os.path.dirname(os.path.realpath(__file__))



def main(t_control):

    ### LOG VARIABLES ###

    saved_db = OrderedDict() # Log is a dictionary, key is trial number, value is a tuple with all parameters: (thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)

    responses = np.zeros(1) # Array (will get extended) keeping track of all responses.    
    pd_log = pd.DataFrame() # pandas log for online analysis


    # Initialize timestamps
    START_TIME = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    clock = core.MonotonicClock()
    sample = t_control.sample_gabor

    for trial in range(num_trials):    
        
        trial_angles = t_control.prepare_trial() # Generates angles from shuffled list
         
        t_type, probe_angle, angle_bin, first_angle = trial_angles['t_type'], trial_angles['probe_angle'], trial_angles['angle_bin'],trial_angles['first_angle'] 

        # COLOR FRAME for trial type, hold (DMTS) or drop (control)
       # t_control.toggle_frame(True)
        if(t_type == 'control'):
           # t_control.set_frame_color('DarkRed')
            gui.set_fixation_color('Red')

        else:
            #t_control.set_frame_color('DarkGreen')
            gui.set_fixation_color('Green')

        
        #### ITI ####
        ITI_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        ITI_time_psychopy = clock.getTime()

        for frame in range(int(ITI * refresh_rate)):
            params.win.flip()
        

        #### TARGET ####
        #OREINTAION SET IN gabor_params in prepare_trial()
        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        target_appeared_psychopy = clock.getTime()
        
        # SET SAMPLE OREINATATION HERE
        
        for frame in range(int(sample_presentation_time * refresh_rate)):

            if(frame % phase_frames == 0):
                sample.setPhase(phase_step, '+')

            sample.draw() # First cue,
                
            if(LIGHT_SENSOR): t_control.sensor_square.draw()
            
            params.win.flip()

    
        ### ISI ###
        
        ISI_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        ISI_time_psychopy = clock.getTime()
        
        for frame in range(int(ISI * refresh_rate)):
           # if frame == int(ISI * refresh_rate / 10.0) : t_control.toggle_frame(False) # Hide the frame informing about trial type

            params.win.flip() #Empty screen, only fixation cross
        
        if t_type == 'control': 
            saved_db[trial] = {'trial_logged' : trial,
                                 'trial_type' : t_type, 
                                 'angle_bin' : angle_bin, 
                                 'first_angle' : first_angle,
                                 'ITI_time' : ITI_time, 
                                 'ITI_time_psychopy' : ITI_time_psychopy,
                                 'target_time' : target_appeared,
                                 'target_time_psychopy' : target_appeared_psychopy,
                                 'ISI_time' : ISI_time, 
                                 'ISI_time_psychopy' : ISI_time_psychopy,
                                 'start_time' : START_TIME
                            }
            
            pd_log = log_trial(pd_log, trial, **saved_db[trial])
            
            #t_control.toggle_frame(False)
            gui.set_fixation_color('white')
                    ### ITI 2###
            for frame in range(int( ITI_2 * refresh_rate)):
                params.win.flip() # Draw an empty screen for short period after probe and then show the anwsers's instructions

            continue

        #### PROBE ####
        sample.setOri(sample.ori + probe_angle) # CHANGE THE ORIENTATION TO MATCH OR NO-MATCH 
        
        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        probe_appeared_psychopy = clock.getTime()
        
        for frame in range(int(probe_time * refresh_rate)):

            if(frame % phase_frames == 0):
                sample.setPhase(phase_step, '+')

            sample.draw() # Second gabor
            if(LIGHT_SENSOR) : t_control.sensor_square.draw()
            params.win.flip()


        ### EMPTY ###
        for frame in range(int(response_wait * refresh_rate)):
            params.win.flip() # Draw an empty screen for short period after probe and then show the anwsers's instructions


        ### RESPONSE ###
        #t_control.toggle_frame(False)

        gui.set_fixation_color('white')

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
                    
                if thisKey== 'num_4' or thisKey== 'a' :
                    thisResp = 'left'
                    correct = check_response(thisResp, t_type, order)
                
                if thisKey == 'num_5' or thisKey== 's':
                    thisResp = 'middle'
                    correct = 'dont know'
                    print('dont know')

                        
                elif thisKey == 'num_6' or thisKey== 'd':
                    thisResp = 'right'
                    correct = check_response(thisResp, t_type, order)

        
                elif thisKey in ['escape']:
                    OnQuit(pd_log, saved_db)
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment        

        # Time of keypress
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        key_time_psychopy = clock.getTime()

        
        responses = np.append(responses, thisResp)
        
        
        saved_db[trial] = { 'trial_logged' : trial,
                            'angle_bin' : angle_bin, 
                            'first_angle' : first_angle,
                            'raw_key' : thisKey,
                            'response' : thisResp,
                            'accuracy' : correct,
                            'ITI_time' : ITI_time,
                            'ITI_time_psychopy' : ITI_time_psychopy,
                            'ISI_time' : ISI_time, 
                            'ISI_time_psychopy' : ISI_time_psychopy,
                            'instruction_time' : instruction_appeared_time,
                            'instruction_time_psychopy' : instruction_appeared_time_psychopy,
                            'order' : order, 
                            'trial_type' : t_type,
                            'precise_angle' : probe_angle, 
                            'target_time' : target_appeared,
                            'target_time_psychopy' : target_appeared_psychopy,
                            'probe_time' : probe_appeared,
                            'probe_time_psychopy' : probe_appeared_psychopy,
                            'key_time' : key_time,
                            'key_time_psychopy' : key_time_psychopy,
                            'participant' : params.expInfo['participant'],
                            'start_time' : START_TIME
                            }
    
                            
        
        pd_log = log_trial(pd_log, trial, **saved_db[trial])
        
        gui.toggle_fixation() # Turn fix off

        ### ITI 2###
        for frame in range(int( ITI_2 * refresh_rate)):
            params.win.flip() # Draw an empty screen for short period after probe and then show the anwsers's instructions


    
    params.win.close()
    
    # Saves the logs   
    OnQuit(pd_log, saved_db)
    
    core.quit()
    
    
def log_trial(pd_log, trial, **kwargs):
    
    pd_log = pd_log.append(pd.DataFrame(kwargs, [trial]))
    
    return pd_log


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

def OnQuit(pd_log, saved_db):
    """Called at the end of script and saves logs to disk"""    
    print('Saving logs')
    pd_log.to_csv(dir_path +'/exp_logs/'+ params.expInfo['participant'] + '.csv', index_label = 'index_copy')
    with open(dir_path + '/exp_logs/' + params.expInfo['participant'] + datetime.now().strftime('_%Y_%m_%d_') + 'log.pickle', 'wb') as handle:
        pickle.dump(saved_db, handle)
    print('logs saved')
def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)
    
if __name__ == '__main__':
    main(trial_controler)
