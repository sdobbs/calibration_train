#!/bin/bash

if [ -z "$1" ]; then
    echo no run specified, skipping tagger calibrations...
    exit 0
fi

run=$1

echo ==run $run==
hd_root --nthreads=20 -POUTPUT_FILENAME=hd_root_r${run}-tagger.root -PPLUGINS=TAGM_TW -PTAGMHit:DELTA_T_ADC_TDC_MAX=300 /gluonraid2/rawdata/volatile/RunPeriod-2018-01/rawdata/Run0${run}/hd_rawdata_0${run}_*.evio
python timing.py -b hd_root_r${run}-tagger.root ${run} rf default
python tw.py -b hd_root_r${run}-tagger.root ${run}
ccdb add PHOTON_BEAM/microscope/fadc_time_offsets -r ${run}-${run} adc_offsets-${run}.txt
ccdb add PHOTON_BEAM/microscope/tdc_time_offsets -r ${run}-${run} tdc_offsets-${run}.txt
ccdb add PHOTON_BEAM/microscope/tdc_timewalk_corrections -r ${run}-${run} tw-corr-${run}.txt

exit 0
