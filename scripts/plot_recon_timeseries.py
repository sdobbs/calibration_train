## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TGraph,TF1,TCanvas
import rcdb
from optparse import OptionParser
from array import array

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"     # to have a name in logs

    return provider


def main():
    # Defaults
    OUTPUT_FILENAME = "out.root"
    #RCDB_QUERY = "@is_production and @status_approved"
    RCDB_QUERY = "@is_2018production and @status_approved"
    VARIATION = "default"
    BEGINRUN = 1
    ENDRUN = 100000000

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    parser.add_option("-b","--begin-run", dest="begin_run",
                     help="Starting run for output")
    parser.add_option("-e","--end-run", dest="end_run",
                     help="Ending run for output")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 1):
        parser.print_help()
        sys.exit(0)

    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)


    # Load CCDB
    #ccdb_conn = LoadCCDB()
    #table = ccdb_conn.get_type_table(CCDB_TABLE)
    #nentries = len(table.columns)
    #print (table)
    #print(table.path)
    #print(table.columns)
    #exit(0)

    # Load RCDB
    rcdb_conn = None
    try:
        rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    except:
        e = sys.exc_info()[0]
        print "Could not connect to RCDB: " + str(e)
    
    # get run list
    runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY, BEGINRUN, ENDRUN) ]
    runs_arr = array('f')
    runs_arr.fromlist(runs)

    c1 = TCanvas("c1","c1",800,600)

    nrho = array('f') 
    nomega = array('f') 

    nrho_ps = array('f') 
    nomega_ps = array('f') 
    omega_res = array('f') 
    omega_res_nokinfit = array('f') 

    c1.Print("out.pdf[")

    # Fill data
    for run in runs:
        print "==%d=="%run
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver21/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver30/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver30/rootfiles/hd_root_%06d.root"%run)
        f = TFile("/work/halld/data_monitoring/RunPeriod-2018-08/mon_ver14/rootfiles/hd_root_%06d.root"%run)

        #print "== /cache/halld/RunPeriod-2017-01/calib/ver14/hists/Run%06d/hd_calib_verify_Run%06d_001.root =="%(run,run)

        # BCAL
        try:
            locHist_NumEvents = f.Get("p2pi_preco_kinfit/NumEventsSurvivedAction");
            n_triggers_rho = locHist_NumEvents.GetBinContent(1);

            #locHist_PSPairs_E = f.Get("PSPair/PSC_PS/PS_E")
            locHist_PSPairs_E = f.Get("PS_flux/PSC_PS/PS_E")
            n_ps = locHist_PSPairs_E.Integral()
            #locHist_PSPairs_E = f.Get("PS_flux/psflux_num_events")
            #n_ps = locHist_PSPairs_E.GetBinContent(1)

        except:
            nrho.append(0)
            nomega.append(0)
            nrho_ps.append(0)
            nomega_ps.append(0)
            omega_res.append(0)
            omega_res_nokinfit.append(0)
            continue

        # rho
        locHist_RhoMass_KinFitCut = f.Get("p2pi_preco_kinfit/Hist_InvariantMass_Rho_PostKinFitCut/InvariantMass")
        n_rho = locHist_RhoMass_KinFitCut.Integral(200, 700);

        # omega
        locHist_NumEvents = f.Get("p3pi_preco_any_kinfit/NumEventsSurvivedAction");
        n_triggers_omega = locHist_NumEvents.GetBinContent(1);

        locHist_Omega_KinFitCut =  f.Get("p3pi_preco_any_kinfit/Hist_InvariantMass_Omega_PostKinFitCut/InvariantMass")
        n_omega = locHist_Omega_KinFitCut.Integral(100, 400)


        nrho.append( n_rho/n_triggers_rho*1000. )
        nomega.append( n_omega/n_triggers_omega*1000. )

        if n_rho/n_ps*1000. < 20.:
            nrho_ps.append( n_rho/n_ps*10000. )
            nomega_ps.append( n_omega/n_ps*10000. )
        else:
            nrho_ps.append( n_rho/n_ps*1000. )
            nomega_ps.append( n_omega/n_ps*1000. )

        locHist = f.Get("p3pi_preco_any_kinfit/Hist_InvariantMass_Omega_PostKinFitCut/InvariantMass")
        locHist.Rebin(5);
        maximum = locHist.GetBinCenter(locHist.GetMaximumBin());
        fr = locHist.Fit("gaus", "SQ", "", maximum - 0.05, maximum + 0.05);

        omega_res.append( 1000.*fr.Parameter(2) )

        locHist = f.Get("p3pi_preco_any_kinfit/Hist_InvariantMass_Omega/InvariantMass")
        locHist.Rebin(5);
        maximum = locHist.GetBinCenter(locHist.GetMaximumBin());
        fr = locHist.Fit("gaus", "SQ", "", maximum - 0.05, maximum + 0.05);

        omega_res_nokinfit.append( 1000.*fr.Parameter(2) )

        locHist.Draw()
        c1.Print("out.pdf")



    c1.Print("out.pdf]")

    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    # write out graphs
    rho_gr = TGraph(len(runs_arr), runs_arr, nrho)
    rho_gr.SetName("nrho")
    rho_gr.SetTitle("# rho's/1k triggers vs. run number")
    rho_gr.Write()

    omega_gr = TGraph(len(runs_arr), runs_arr, nomega)
    omega_gr.SetName("nomega")
    omega_gr.SetTitle("# omega's/1k triggers vs. run number")
    omega_gr.Write()

    omega_res = TGraph(len(runs_arr), runs_arr, omega_res)
    omega_res.SetName("omega_res")
    omega_res.SetTitle("omega resolutions")
    omega_res.Write()

    omega_res_nokinfit = TGraph(len(runs_arr), runs_arr, omega_res_nokinfit)
    omega_res_nokinfit.SetName("omega_res_nokinfit")
    omega_res_nokinfit.SetTitle("omega resolutions")
    omega_res_nokinfit.Write()

    rho_ps_gr = TGraph(len(runs_arr), runs_arr, nrho_ps)
    rho_ps_gr.SetName("nrho_ps")
    rho_ps_gr.SetTitle("# rho's/1k PS Pairs vs. run number")
    rho_ps_gr.Write()

    omega_ps_gr = TGraph(len(runs_arr), runs_arr, nomega_ps)
    omega_ps_gr.SetName("nomega_ps")
    omega_ps_gr.SetTitle("# omega's/1k PS Pairs vs. run number")
    omega_ps_gr.Write()


    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
