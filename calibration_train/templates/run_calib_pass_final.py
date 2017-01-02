# script for pass 1 calibration processing

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
        # Create monitoring information
        #hdmon_root_utils.run_root_commands([".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/FitScripts/ExtractTDCADCTiming.C(%d)"%(int(os.environ["RUN"]))])
        hdmon_root_utils.run_root_commands([".x $HALLD_HOME/src/plugins/Calibration/st_tw_corr_auto/macros/st_tw_resols.C(\"%s\")"%("hd_root.root")])
        hdmon_root_utils.run_root_commands([".x $HALLD_HOME/src/plugins/Calibration/TAGH_timewalk/scripts/gaussian_fits.C(\"%s\",false)"%("hd_root.root")])
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_TaggerComparison.C"], 
                                          "final_RF_TaggerComparison.png")
        # HLDetectorTiming plots
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_CalorimeterTiming.C"],
                                          "final_HLDT_CalorimeterTiming.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_PIDSystemTiming.C"],
                                          "final_HLDT_PIDSystemTiming.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment.C"],
                                          "final_HLDT_TaggerRFAlignment.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerSCAlignment.C"],
                                          "final_HLDT_TaggerSCAlignment.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerTiming.C"],
                                          "final_HLDT_TaggerTiming.png")
        hdmon_root_utils.run_calib_script(input_file, 
                                          [".x $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackMatchedTiming.C"],
                                          "final_HLDT_TrackMatchedTiming.png")

    # cleanup
    input_file.Close()
