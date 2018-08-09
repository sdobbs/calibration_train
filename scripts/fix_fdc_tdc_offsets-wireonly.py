## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
import rcdb
from optparse import OptionParser
from array import array
import pprint
import math

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

from ROOT import TFile,TH1I,TH2I,TCanvas


def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    return provider


def FindFDCPackageChamber(plane):
    package = plane / 6 + 1
    chamber = plane % 6
    if(chamber == 0):
        chamber = 6
        package -= 1
  
    return (package, chamber)


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    RCDB_QUERY = ""
    RCDB_QUERY = "@is_2018production and status != 0"
    #RCDB_QUERY = "@is_2018production"
    #RCDB_QUERY = "@is_2018production and @status_approved"
    VARIATION = "default"

    MAKE_PLOTS = False

    BEGINRUN = 30000
    ENDRUN = 39999

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-F","--run_file", dest="run_file", 
                      help="File of runs to look at")
    parser.add_option("-V","--variation", dest="variation", 
                      help="CCDB variation to use")
    parser.add_option("-b","--begin_run", dest="begin_run",
                      help="Starting run when scanning RCDB")
    parser.add_option("-e","--end_run", dest="end_run",
                      help="Ending run when scanning RCDB")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    #if(len(args) < 1):
    #    parser.print_help()
    #    sys.exit(0)

    if options.variation:
        VARIATION = options.variation
    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # get run list
    runs = []

    if MAKE_PLOTS:
        c1 = TCanvas("c1","c1",800,600)
        c1.Print("out.pdf[")

    if options.run_file:
        with open(options.run_file) as f:
            for line in f:
                try:
                    runs.append(int(line.strip()))
                except:
                    print "Ignoring line: "+line
    else:
        # Load RCDB
        rcdb_conn = None
        try:
            rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
            runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY, BEGINRUN, ENDRUN) ]
        except:
            e = sys.exc_info()[0]
            print "Could not connect to RCDB: " + str(e)
    

    # Print to screen
    for run in runs:
        print "===%d==="%run

        # find the offset relative to the base FDC time
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver13/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver06/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver16/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        f = TFile("/group/halld/Users/sdobbs/hd_root.root")

        # see if the files exists
        try:
            hfdctdc = f.Get("HLDetectorTiming/FDC/FDCHit Wire time vs. module")
            maximum = hfdctdc.GetBinCenter(hfdctdc.GetMaximumBin());
        except:
            print "fail 1"
            continue

        #fdcTimeHist = f.Get("/HLDetectorTiming/TRACKING/Earliest Flight-time Corrected FDC Time")
        #MPV = 0;
        #try:
        #    maximum = fdcTimeHist.GetBinCenter(fdcTimeHist.GetMaximumBin());
        #    fr = fdcTimeHist.Fit("landau", "S", "", maximum - 2.5, maximum + 4);
        #    MPV = fr.Parameter(1);
        #except:
        #    print "fail 2"
        #    pass

        tdc_toff_assignments = []
        tdc_toff_assignments.append( ccdb_conn.get_assignment("/FDC/package1/wire_timing_offsets", run, VARIATION) )
        tdc_toff_assignments.append( ccdb_conn.get_assignment("/FDC/package2/wire_timing_offsets", run, VARIATION) )
        tdc_toff_assignments.append( ccdb_conn.get_assignment("/FDC/package3/wire_timing_offsets", run, VARIATION) )
        tdc_toff_assignments.append( ccdb_conn.get_assignment("/FDC/package4/wire_timing_offsets", run, VARIATION) )
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        tdc_offsets = []
        tdc_offsets.append( tdc_toff_assignments[0].constant_set.data_table )
        tdc_offsets.append( tdc_toff_assignments[1].constant_set.data_table )
        tdc_offsets.append( tdc_toff_assignments[2].constant_set.data_table )
        tdc_offsets.append( tdc_toff_assignments[3].constant_set.data_table )

        # let's find the changes to make
        hfdctdc = f.Get("HLDetectorTiming/FDC/FDCHit Wire time vs. module")

        try:
            n = hfdctdc.GetNbinsX()
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue


        package_times_shifted = [ False, False, False, False ]

        #print 1,"  ",(hfdctdc.GetNbinsX()/2+1)

        for plane in xrange(1,hfdctdc.GetNbinsX()/2+1):
            projY = hfdctdc.ProjectionY("temp_%d"%(2*plane-1), 2*plane-1, 2*plane-1);
            maximum = projY.GetBinCenter(projY.GetMaximumBin());
            mean1 = 0.;
            if(maximum > -190.):
                mean1 = maximum 

            if MAKE_PLOTS:
                projY.Draw()
                c1.Print("out.pdf")

            projY = hfdctdc.ProjectionY("temp_%d"%(2*plane), 2*plane, 2*plane);
            maximum = projY.GetBinCenter(projY.GetMaximumBin());
            mean2 = 0.;
            if(maximum > -190.):
                mean2 = maximum 

            if MAKE_PLOTS:
                projY.Draw()
                c1.Print("out.pdf")

            #if( (abs(mean1) < 5.) and (abs(mean2) < 5.) ):
            #    continue
       
            (package, chamber) = FindFDCPackageChamber(plane)
            print package," ",chamber," ",mean1," ",mean2
            package_times_shifted[package-1] = True;
       
            #if(abs(mean1) > 5.):
            for wire in xrange(48):
                #tdc_offsets[package-1][chamber-1][wire] = str( float(tdc_offsets[package-1][chamber-1][wire]) + float(mean1) );
                tdc_offsets[package-1][chamber-1][wire] = mean1;
            #if(abs(mean2) > 5.):
            for wire in xrange(48):
                #tdc_offsets[package-1][chamber-1][wire+48] = str( float(tdc_offsets[package-1][chamber-1][wire]) + float(mean2) );
                tdc_offsets[package-1][chamber-1][wire+48] = mean2;


        #break
        #continue

        # save results
        if( (package_times_shifted[0]==False) and (package_times_shifted[1]==False) and (package_times_shifted[2]==False) and (package_times_shifted[3]==False) ):
            continue

        print "commit corrections..."

        for package in xrange(4):
            #pp.pprint(tdc_offsets[package])
            #continue
            if(not package_times_shifted[package]):
                continue

            print "package %d"%(package+1)

            ccdb_conn.create_assignment(
                data=tdc_offsets[package],
                path="/FDC/package%d/wire_timing_offsets"%(package+1),
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to TDC module shifts")


    if MAKE_PLOTS:
        c1.Print("out.pdf]")

## main function 
if __name__ == "__main__":
    main()
