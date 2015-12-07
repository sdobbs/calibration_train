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
        print "Running RFMacro_FineTimeOffsets.C"
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C(%d,\"%s\")"%(int(os.environ["RUN"]),"calib_pass0")], 
                                          "pass0_RF_FineTimeOffsets.png")

        #hdmon_root_utils.run_root_commands([".L $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_TaggerComparison.C", "main();"])  # for final

        # cleanup
        input_file.Close()
