#!/bin/bash

if [ -z "$1" ]; then
    echo no run specified, skipping tagger calibrations...
    exit 0
fi

run=$1

# actually update the master DB
export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb
export CCDB_USER=hdsys

# diagnostics
echo CCDB_CONNECTION=$CCDB_CONNECTION
echo JANA_CALIB_URL=$JANA_CALIB_URL

# run data
echo ==tagger pass1: run $run==
hd_root -PEVENTS_TO_SKIP=100 --nthreads=35 -PJANA:BATCH_MODE=1 -POUTPUT_FILENAME=hd_root_r${run}-tagger.root -PPLUGINS=TAGM_TW,PS_timing -PTAGMHit:DELTA_T_ADC_TDC_MAX=100 /gluonraid2/rawdata/volatile/RunPeriod-2019-11/rawdata/Run0${run}/hd_rawdata_0${run}_*.evio
python tagm_timing.py -b hd_root_r${run}-tagger.root ${run} rf default
python tagm_tw.py -b hd_root_r${run}-tagger.root ${run}
./ps_run.sh ${run} hd_root_r${run}-tagger.root

echo ==submit TAGM constants==
ccdb add /PHOTON_BEAM/microscope/fadc_time_offsets -v default -r ${run}-${run} adc_offsets-${run}.txt
ccdb add /PHOTON_BEAM/microscope/tdc_time_offsets -v default -r ${run}-${run} tdc_offsets-${run}.txt
ccdb add /PHOTON_BEAM/microscope/tdc_timewalk_corrections -v default -r ${run}-${run} tw-corr-${run}.txt
echo ==submit PS constants==
ccdb add /PHOTON_BEAM/pair_spectrometer/base_time_offset -v default -r ${run}-${run} ps_offsets/base_time_offset.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/tdc_timing_offsets -v default -r ${run}-${run} ps_offsets/tdc_timing_offsets_psc.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/adc_timing_offsets -v default -r ${run}-${run} ps_offsets/adc_timing_offsets_psc.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/fine/adc_timing_offsets -v default -r ${run}-${run} ps_offsets/adc_timing_offsets_ps.txt



echo ==tagger pass2: run $run==
hd_root  -PEVENTS_TO_SKIP=100  --nthreads=35 -PJANA:BATCH_MODE=1 -POUTPUT_FILENAME=hd_root_r${run}-tagger-p2.root -PPLUGINS=TAGH_timewalk /gluonraid2/rawdata/volatile/RunPeriod-2019-11/rawdata/Run0${run}/hd_rawdata_0${run}_*.evio
./do_tagh.sh ${run} hd_root_r${run}-tagger-p2.root

echo ==submit TAGH constants==
ccdb add PHOTON_BEAM/hodoscope/tdc_timewalk -v default -r ${run}-${run} tdc_timewalk.txt

exit 0
