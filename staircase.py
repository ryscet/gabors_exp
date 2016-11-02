#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment:
    Show a series of gabor patches pairs. First gabor is the target, sceond is the probe. Subjects reply whether the probe is identical to the target. 
    

Staricase:
    After successfull discrimination the difficulty is increased. After failure to detect a difference the difficulty is decreased. Setting the amount of conseciutive successess and failures to change the difficulty will result in different threshold produced by the staircase procedure. We use 2 consecutive sucesses to increase difficulty and single failure to decrease. 2:1 ratio produces outcome sucess rate of 70.7%. p ** n = .5 where n is the amount of consecutive successes to increase difficulty. Formula valid only for cases where single error decreases difficulty (Levitt, 1971 Transformed up-down in psychoacustics). 

After a difficulty is determined a small noise is added to the angle change and a coin toss determines the sign of the angle.

There is a predefined amount of trials - i.e. no guarantee of convergence and perhaps too long
"""

import pandas as pd
from datetime import datetime
import numpy as np
from collections import OrderedDict
from psychopy import event, core
import pickle 

import stair_params as params
import explore_results 


# The gabor which appears first
target = params.instructions_params()
# Second gabor which is compared to the target and answered if it is the same
probe = params.main_stimulus()

# indexes step_list, the larger the bigger the task difficutly, i.e. the smaller the angle difference to detect
diff_index = 0

# List of angle differences to apply between the target and the probe. Staircase function then uses a toincoss to either use a negative or positive value with magnitude defiuned by step list. Staircase also adds a small jitter to step_list values.
step_list = [20, 15, 10, 8, 6, 4, 3, 2.5, 2, 1.5, 1.25, 1.0, 0.75, 0.5, 0.0, 0.0]

# Array (will be extended) keeping track of all responses.
responses = np.zeros(1)

# Used to calculate the staircase output. Clear after each staircase decision.
last_two_responses = []

# First draft of staircase length, use fixed num of trials
num_trials = len(step_list) * 2 + 20 # + 18 allows for 8 mistakes to still get to the end
#aaanum_trials = 3
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


def OnQuit():
    
    pd_log.to_csv('stair_logs/'+ params.expInfo['participant'] + '.csv', index_label = 'index_copy')
    with open('stair_logs/' + params.expInfo['participant'] + datetime.now().strftime('_%Y_%m_%d_') + 'log.pickle', 'wb') as handle:
        pickle.dump(saved_db, handle)
    
    try:
        explore_results.plot_staircase(params.expInfo['participant'])
    except:
        print('developing probably')


def staircase():
    """ Reads the last two responses and determines whether and how to change difficulty level. 
    If there were to consecutive correct responses increase difficulty.
    If there was a single error decrease difficulty.
    If there was one correct reponses do nothing.
    Will converge on stimulus energy producing 70.7% correct detections.
    
    """
    global last_two_responses
    global diff_index
    global angle
#NOTE: Decrementing difficulty has to be first, otherwise it will always be true after increment difficulty is also true, because it will reset the last_two_responses to 0

    # decrement difficulty if there was an error. 
    if responses[-1] == 0:
        # try to decrement it, otherwise keep at minimum
        if(diff_index >= 1):

            diff_index = diff_index -1
        else:
            diff_index = 0
        print('decreasing')
        # clear immediate history 
        last_two_responses = [] 
    
    # increment difficulty after tow consecutve successess
    elif np.array(last_two_responses).sum() == 2:
        # Try to increment it otherwise keep at maximum
        if(diff_index < len(step_list) - 1):

            diff_index = diff_index +1
        else:
            diff_index = len(step_list) - 1
        print('increasing')
        
        # clear immediate history 
        last_two_responses = []
    
    # Choose an angle based on the current difficulty level and add small noise to it
    angle = np.random.normal(step_list[diff_index], scale = 0.01)
    
    
    # Toss a coin to choose the angle either in clockwise or counterclockwise direction
    if(np.random.choice([True, False])):
        angle = angle * -1
    
    return angle

def choose_target_orientation():
    """Small helper function for selecting and deleting from a list (pre-shuffled)"""
    global orientation
    orientation = target_orientations[-1]
    del target_orientations[-1]
    return orientation

def main():
    
    global responses
    global last_two_responses
    global pd_log
    
    for trial in range(num_trials):    
    
        #### TARGET ####
    
        # Draw the target frame
        # TODO: maybe there are other ways to indicate what is the target and what is the probe
    #    target.circle.draw()
        
        # Select tartget angle from a uniform list of angles between 0 and 360.
        target.grating.setOri(choose_target_orientation())
        target.grating.draw()
        
        target_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    
        # Draw the target onscreen and wait for its duration
        params.win.flip()
        core.wait(target_presentation_time)
    
        # ISI
        params.win.flip()
        
        core.wait(ISI)
        
        #### PROBE ####
        
        # Change probe orientation by calling staircase
        probe.grating.setOri(target.grating.ori + staircase())    
        # Draw the probe    
        probe.grating.draw()
        
        params.win.flip()
        
        # mark stimulus time # TODO use psychopy logger
        probe_appeared = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    
        core.wait(probe_time)
        # Draw an empty screen for short period after probe and then show the answer instructions
        params.win.flip()
        
        core.wait(0.2)
    
        target.instruction_red.draw()
        target.instruction_blue.draw()
        
        params.win.flip()
    
        # wait for response
        
        thisResp=None
        while thisResp==None:
            
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                    
                if thisKey=='a':
                    print('right')
                    thisResp = 1
                        
                elif thisKey == 'l':
                    print('wrong')
                    thisResp = 0
        
                elif thisKey in ['escape']:
                    OnQuit()
                    event.clearEvents() #must clear other (eg mouse) events - they clog the buffer
                    params.win.close()
                    core.quit() #abort experiment
        key_time = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        
        # Calc response time
        response_time = (key_time - probe_appeared).total_seconds()
            
        saved_response_times.append(response_time)
        
        last_two_responses.append(thisResp)
        responses = np.append(responses, thisResp)
        
        saved_db[trial] = { 'trial' : trial,
                            'accuracy' : thisResp, 
                            'response_time' : response_time, 
                            'difficulty_level' : diff_index, 
                            'raw_angle' : step_list[diff_index],
                            'used_angle' : angle, 
                            'target_orientaion' : orientation,
                            'target_time' : target_appeared,
                            'probe_time' : probe_appeared,
                            'key_time' : key_time,
                            'participant' : params.expInfo['participant']}
                            
        pd_log = pd_log.append(pd.DataFrame(saved_db[trial], [trial]))
        
        params.win.flip()
    
        # ITI
        core.wait(ITI)
    
    
    params.win.close()
    
    # Saves the logs   
    OnQuit()
    
    core.quit()

if __name__ == '__main__':
    main()
