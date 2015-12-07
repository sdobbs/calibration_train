# Utility functions for job management
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015


def GetRunPeriodFromRun(run):
    # mapping between run range names and (low run, high run) pairs
    RunPeriod_Run_Map = {
        "RunPeriod-2014-10" : (  630, 2439 ),
        "RunPeriod-2015-01" : ( 2440, 2606 ),
        "RunPeriod-2015-03" : ( 2607, 3385 ),
        "RunPeriod-2015-06" : ( 3386, 9999999 ) 
        }

    # perform a linear search through the mapping
    for (run_period, run_range) in RunPeriod_Run_Map.items():
        if(run>=run_range[0] and run<=run_range[1]):
            the_run_period = run_period
    if the_run_period is None:
        the_run_period = ""
    return the_run_period
