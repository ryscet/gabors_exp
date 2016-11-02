#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment:
    Show a series of gabor patches pairs. First gabor is the target, sceond is the probe. Subjects reply whether the probe is identical to the target. 
    
"""

import pandas as pd
from datetime import datetime
import numpy as np
from collections import OrderedDict
from psychopy import event, core
import pickle 
import random 
import os 
import glob


import exp_params as params


# The gabor which appears first
target = params.instructions_params()
# Second gabor which is compared to the target and answered if it is the same
probe = params.main_stimulus()

# angle value changing on each trial with pseduo random sfuffle, will include values found by staircase, 0 and big differences
angle = 0

# Value used for the type of trials where the difference should be clearly visible
big_angle = 10

# Array (will be extended) keeping track of all responses.
responses = np.zeros(1)

# First draft of staircase length, use fixed num of trials
num_trials = 30

# Create a list of angles to be used as target. This will be random uniform between 0 and 360 degrees.
target_orientations = list(np.random.uniform(0, 360, num_trials +1))

# used to store rt's
saved_response_times = []

# Log is a dictionary, key is trial number, value is a tuple with all parameters 
#(thisResp, response_time, diff_index, step_list[diff_index], angle, orientation)
saved_db = OrderedDict()
# pandas log for immediate analysis
pd_log = pd.DataFrame()

target_presentation_time = 2.0 # onscreen target
ISI = 1.0 # empty screen between target and probe
probe_time = 0.2 # probe onscreen time
ITI = 2.0 # between trial (from response untill new target)



    


def main():
    
    # Pseudo random shuffled list of probe angles
    angle_list, codes_list = create_angles()

    global responses
    global last_two_responses
    global pd_log
    
    for trial in range(num_trials):    
    
        #### TARGET ####
    
        # Select tartget angle from a uniform list of angles between 0 and 360.
        target.grating.setOri(choose_target_orientation())
        target.grating.draw()
        
        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    
        # Draw the target onscreen and wait for its duration
        params.win.flip()
        core.wait(target_presentation_time)
    
        ### ISI ###
        params.win.flip()
        
        core.wait(ISI)
        
        #### PROBE ####
        
        # Change probe orientation by adding the value from angle list
        angle = select_probe_angle(angle_list, trial)
        probe.grating.setOri(target.grating.ori + angle)
        
        # Draw the probe    
        probe.grating.draw()
        
        params.win.flip()
        
        # mark stimulus time # TODO use psychopy logger
        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    
        core.wait(probe_time)
        
        ### EMPTY ###
        
        # Draw an empty screen for short period after probe and then show the answer instructions
        params.win.flip()
        
        core.wait(0.2)
    
        target.instruction_red.draw()
        target.instruction_blue.draw()
        
        params.win.flip()
    
        #### RESPONSE ####
        
        thisResp=None
        while thisResp==None:
            
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                    
                if thisKey=='a':
                    thisResp = 1
                        
                elif thisKey == 'l':
                    thisResp = 0
        
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
                            'response' : thisResp, 
                            'response_time' : response_time, 
                            'raw_angle' : codes_list[trial],
                            'used_angle' : angle, 
                            'target_orientaion' : orientation,
                            'target_time' : target_appeared,
                            'probe_time' : probe_appeared,
                            'key_time' : key_time,
                            'participant' : params.expInfo['participant']}
    
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
        
        params.win.flip()
    
        #### ITI ####
        core.wait(ITI)
    
    
    params.win.close()
    
    # Saves the logs   
    OnQuit()
    
    core.quit()

    
def create_angles():
    
    # Define proportion of trials for each angle value
    num_stair = int(num_trials * 0.5)
    num_big = int(num_trials * 0.25)
    num_zero = int(num_trials * 0.25)
    
    # int always rounds down, so there will usually be some trials unnasignedd. Add them to stair trials
    num_stair = num_stair + (num_trials - num_big - num_zero - num_stair )
    
    #load the staircase results
    results = pd.read_csv(find_latest_log())
    # calculate the average of the last two levels used, this will either be the last stable success (upper bound) or include the error, i.e. lower bound
    threshold = results.tail(2)['raw_angle'].mean()

    # Add the angle values in the amounts specified bu num trials proportions
    angle_list = [0 for z in range(num_zero)]
    angle_list.extend([np.random.normal(big_angle , scale = 2) for b in range(num_big)])
    angle_list.extend([threshold for s in range(num_stair)])
    
    # Because the angles have some random noise, create a corresponding category list for easier analysis (groupby)
    codes_list = ['zero' for z in range(num_zero)]
    codes_list.extend(['big' for z in range(num_big)])
    codes_list.extend(['threshold' for z in range(num_stair)])
    
    # reorder the list
    c = list(zip(angle_list, codes_list))

    random.shuffle(c)

    angle_list, codes_list = zip(*c)
    
    
    return list(angle_list), list(codes_list)
    
    
def find_latest_log():
    """Browses all logs from staircase procedure and selects the last one, i.e. the one for the current participant."""
    # List all paths for logs
    paths = glob.glob('stair_logs/*.csv')
    # Find the index where the log has the largets, i.e. latest, modification time (cross platform in comparison to creation time)
    last_file_idx = np.argmax(np.array([os.path.getmtime(path) for path in paths]))
    # Select the latest path
    last_file_path = paths[last_file_idx]
  
    return last_file_path 
    
def select_probe_angle(angle_list, trial_index):
    """ Pseudo-random shuffle from a collection of angles defined by staircase, relatively big differences and zero differences
    """
    
    angle = np.random.normal(angle_list[trial_index], scale = 0.01)
    
    # Toss a coin to choose the angle either in clockwise or counterclockwise direction
    if(np.random.choice([True, False])):
        angle = angle * -1
    
    return angle

def choose_target_orientation():
    """Small helper function for selecting and deleting from a list (pre-shuffled)"""
    global orientation
    # Select from targewt orientations list
    orientation = target_orientations[-1]
    # Delete at the index same as selected
    del target_orientations[-1]
    
    return orientation
 

def OnQuit():
    """Called at the end of script and saves logs to disk"""    
    
    pd_log.to_csv('exp_logs/'+ params.expInfo['participant'] + '.csv', index_label = 'index_copy')
    with open('exp_logs/' + params.expInfo['participant'] + datetime.now().strftime('_%Y_%m_%d_') + 'log.pickle', 'wb') as handle:
        pickle.dump(saved_db, handle)
    
        

    
    
if __name__ == '__main__':
    main()
