#!/bin/bash 

RUNMIN=$1
RUNMAX=$2
VARIATION=calib

printenv CCDB_CONNECTION

ccdb add CDC/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX cdc_base_time.txt
#ccdb add FDC/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX fdc_base_time.txt
#ccdb add BCAL/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX bcal_base_time.txt
ccdb add FCAL/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX fcal_base_time.txt
#ccdb add TOF/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX tof_base_time.txt
ccdb add TOF2/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX tof_base_time.txt 
ccdb add START_COUNTER/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX sc_base_time.txt
#ccdb add START_COUNTER/adc_timing_offsets -v $VARIATION -r $RUNMIN-$RUNMAX  sc_adc_timing_offsets.txt
#ccdb add START_COUNTER/tdc_timing_offsets -v $VARIATION -r $RUNMIN-$RUNMAX  sc_tdc_timing_offsets.txt
#ccdb add PHOTON_BEAM/hodoscope/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX tagh_base_time.txt
# only fix run-to-run shifts for the TAGH
#ccdb add PHOTON_BEAM/hodoscope/fadc_time_offsets -v $VARIATION -r $RUNMIN-$RUNMIN tagh_adc_timing_offsets.txt
ccdb add PHOTON_BEAM/microscope/base_time_offset -v $VARIATION -r $RUNMIN-$RUNMAX tagm_base_time.txt
# calibrate the hodoscope for every run
ccdb add PHOTON_BEAM/hodoscope/tdc_time_offsets -v $VARIATION -r $RUNMIN-$RUNMIN tagh_tdc_timing_offsets.txt
ccdb add PHOTON_BEAM/hodoscope/tdc_time_offsets -v default -r $RUNMIN-$RUNMIN tagh_tdc_timing_offsets.txt 2>&1 >> updated_tables.txt
#ccdb add FDC/package1/wire_timing_offsets -v $VARIATION -r $RUNMIN-$RUNMAX fdc_package1_wire_offsets.txt
#ccdb add FDC/package2/wire_timing_offsets -v $VARIATION -r $RUNMIN-$RUNMAX fdc_package2_wire_offsets.txt
#ccdb add FDC/package3/wire_timing_offsets -v $VARIATION -r $RUNMIN-$RUNMAX fdc_package3_wire_offsets.txt
#ccdb add FDC/package4/wire_timing_offsets -v $VARIATION -r $RUNMIN-$RUNMAX fdc_package4_wire_offsets.txt

exit 0
