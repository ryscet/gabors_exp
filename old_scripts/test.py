from psychopy import visual, core, event, monitors #import some libraries from PsychoPy
import pandas as pd
from datetime import datetime
import numpy as np

changeFreq = 10
lastChange = 0
#Define the main application window
mon = monitors.Monitor('dell', width= 54.61, distance=57)
mon.setSizePix([1920, 1080])
win = visual.Window( fullscr = True, winType  ='pyglet', screen =0, waitBlanking = True, checkTiming = True, monitor = mon)

        
def Update(stage, frame):
   # params.grating.setPhase(0.05, '+')#advance phase by 0.05 of a cycle
    if stage == 'main':
        
        change_orientation(frame)        
        
        stim.grating.draw()
        stim.fixation.draw()
    
    if stage == 'instruction':
        target.grating.draw()
        target.instruction.draw()

    
    win.flip()

def change_orientation(currFrame):
    global lastChange
    
    if(currFrame > lastChange + changeFreq):
        new_orient = np.random.uniform(-10 , 10)
        
        stim.grating.setOri(new_orient)
        lastChange = currFrame 


######### MAIN LOOP #############
#                               #
#                               #
#                               #
#########   BELOW   #############

dates = []


target = instructions_params()
stim = main_stimulus()

frame = 0

while frame < 200:
    now = pd.to_datetime(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print(now)
    dates.append(now)
    
    #draw the stimuli and update the window
    if(frame < 100):
        Update('instruction', frame)
    elif((frame > 100) & (frame < 200)):
        Update('main', frame)

    # Quit the loop on keypress
    if len(event.getKeys())>0: break
    event.clearEvents()
    
    frame = frame +1

dates = pd.DataFrame(dates, columns = ['time'])
dates['frame_duration'] = dates['time'] - dates['time'].shift()

#cleanup
win.close()
#core.quit()
