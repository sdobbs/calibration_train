#!/bin/bash

if [ -z "$1" ]; then
    echo no run specified, skipping tagger calibrations...
    exit 0
fi

run=$1

echo ==run $run==
hd_root --nthreads=25 -POUTPUT_FILENAME=hd_root_r${run}-tagger.root -PPLUGINS=TAGM_TW,PS_timing -PTAGMHit:DELTA_T_ADC_TDC_MAX=300 /gluonraid2/rawdata/volatile/RunPeriod-2018-01/rawdata/Run0${run}/hd_rawdata_0${run}_*.evio
python tagm_timing.py -b hd_root_r${run}-tagger.root ${run} rf default
python tagm_tw.py -b hd_root_r${run}-tagger.root ${run}
./ps_run.sh ${run} hd_root_r${run}-tagger.root
ccdb add /PHOTON_BEAM/microscope/fadc_time_offsets -r ${run}-${run} adc_offsets-${run}.txt
ccdb add /PHOTON_BEAM/microscope/tdc_time_offsets -r ${run}-${run} tdc_offsets-${run}.txt
ccdb add /PHOTON_BEAM/microscope/tdc_timewalk_corrections -r ${run}-${run} tw-corr-${run}.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/base_time_offset -v default -r ${run}-${run} ps_offsets/base_time_offset.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/tdc_timing_offsets -v default -r ${run}-${run} ps_offsets/tdc_timing_offsets_psc.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/adc_timing_offsets -v default -r ${run}-${run} ps_offsets/adc_timing_offsets_psc.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/fine/adc_timing_offsets -v default -r ${run}-${run} ps_offsets/adc_timing_offsets_ps.txt
exit 0
