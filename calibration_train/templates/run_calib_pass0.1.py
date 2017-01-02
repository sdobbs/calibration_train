# script for pass 0 calibration processing

import os,sys
import hdmon_root_utils
from ROOT import TFile

if __name__ == "__main__":
    if len(sys.argv)<2:
        print "Need to specify input file on the command line !"
        sys.exit(1)
    
    # tried to open file
    input_file = TFile(sys.argv[1])
    if input_file is None or input_file.IsZombie():
        print "Could not open file: %s"%(sys.argv[1])
        sys.exit(1)

    # load library functions
    hdmon_root_utils.load_calibration_library()

    # RF calibration and monitoring
    if "HALLD_HOME" not in os.environ:
        print "HALLD_HOME not set!"
    else:
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_ROCTITimes.C"],
                                          "pass0_RF_ROCTITimes.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_TDCConversion.C"],
                                          "pass0_RF_TDCConversion.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_SignalPeriod.C"],
                                          "pass0_RF_SignalPeriod.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_BeamBunchPeriod.C"],
                                          "pass0_RF_BeamBunchPeriod.png")

        #hdmon_root_utils.run_root_commands([".L $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_TaggerComparison.C", "main();"])  # for final

        # cleanup
        input_file.Close()
