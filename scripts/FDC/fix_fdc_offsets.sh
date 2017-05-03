#!/bin/bash

while read run; do
    echo ==$run==

    #python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/FitScripts/ExtractTrackBasedTiming.C\(\"/home/gxproj3/volatile/2017-01/hd_root_0${run}.root\",${run},\"default\"\)
    python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/FitScripts/ExtractTrackBasedTiming.C\(\"/cache/halld/RunPeriod-2017-01/calib/ver11/hists/Run0${run}/hd_calib_verify_Run0${run}_001.root\",${run},\"default\"\)


    ccdb add /CDC/base_time_offset -r ${run}-${run}  cdc_base_time.txt
    ccdb add /FDC/base_time_offset -r ${run}-${run}  fdc_base_time.txt
done < runs


