#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Demo of some ways to use class psychopy.info.RunTimeInfo()
to obtain current system and other data at run-time.

https://raw.githubusercontent.com/psychopy/psychopy/master/psychopy/demos/coder/experiment%20control/runtimeInfo.py
"""

from __future__ import division

from psychopy import visual, logging, core
import psychopy.info

from datetime import datetime
import os 
import pickle 


# author and version are used in the demo, in the way you might in your experiment.
# They are expected to be at the top of the script that calls RunTimeInfo()),
# with a string literal assigned to them (no variables).
# double-quotes will be silently removed, single quotes will be left, eg, O'Connor
__author__ = """Ryszard Cetnarski"""
__version__ = "v1.0.a"

# When creating an experiment, first define your window (& monitor):
win = visual.Window(fullscr=True, size=[200, 200], monitor='testMonitor')
win.recordFrameIntervals = True
logging.console.setLevel(logging.DEBUG)

# Then gather run-time info. All parameters are optional:
runInfo = psychopy.info.RunTimeInfo(
        # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
        # author=' < your name goes here, plus whatever you like, e.g., your lab or contact info > ',
        # version=" < your experiment version info > ",
        win=win,    #  # a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating',  #  # None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True,  #  # True means report on everything
        userProcsDetailed=True,  #  # if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
win.close()


print(runInfo)


if "windowRefreshTimeAvg_ms" in runInfo.keys():
    print("or from the test of the screen refresh rate:")
    print("  %.2f ms = average refresh time" % runInfo["windowRefreshTimeAvg_ms"])
    print("  %.3f ms = standard deviation" % runInfo["windowRefreshTimeSD_ms"])

    # Once you have run-time info, you can fine-tune things with the values, prior to running your experiment.
    refreshSDwarningLevel_ms = 0.20  # ms
    if runInfo["windowRefreshTimeSD_ms"] > refreshSDwarningLevel_ms:
        print("\nThe variability of the refresh rate is sort of high (SD > %.2f ms)." % (refreshSDwarningLevel_ms))
        # and here you could prompt the user with suggestions, possibly based on other info:
        if runInfo["windowIsFullScr"]:
            print("Your window is full-screen, which is good for timing.")
            print('Possible issues: internet / wireless? bluetooth? recent startup (not finished)?')
            if len(runInfo['systemUserProcFlagged']):
                print('other programs running? (command, process-ID):' + str(runInfo['systemUserProcFlagged']))
        else:
            print("""Try defining the window as full-screen (it's not currently), i.e. at the top of the demo change to:
    win = visual.Window((800, 600), fullscr=True, ...
and re-run the demo.""")


win.close()
core.quit()

dir_path = os.path.dirname(os.path.realpath(__file__))


with open(dir_path + '/exp_logs/' + datetime.now().strftime('_%Y_%m_%d_') + 'config_info.pickle', 'wb') as handle:
    pickle.dump(runInfo, handle)
# The contents of this file are in the public domain.