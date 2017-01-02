import sys
from optparse import OptionParser

import rcdb
from rcdb.model import ConditionType, Condition, Run


def main():
    # Define command line options
    parser = OptionParser(usage = "update_rcdb_runstatus.py")
    parser.add_option("-p","--password", dest="password", 
                      help="Password to connect to RCDB")
    parser.add_option("-r","--run_number", dest="run_number", 
                      help="Run number to update")
    parser.add_option("-R","--run_range", dest="run_range", 
                      help="Run range to update with format (min,max)")
    parser.add_option("--approve", dest="status_approve", action="store_true",
                      help="Set status to 'approved' (1)")
    parser.add_option("--approve_long", dest="status_approve_long", action="store_true",
                      help="Set status to 'approved_long' (2)")
    parser.add_option("--reject", dest="status_reject", action="store_true",
                      help="Set status to 'rejected' (0)")
    parser.add_option("--unchecked", dest="status_unchecked", action="store_true",
                      help="Set status to 'unchecked' (-1)")
    
    # parse command lines
    (options, args) = parser.parse_args(sys.argv)

    # handle options
    min_run = None
    max_run = None
    status = None

    if options.run_number:
        try:
            min_run = int(options.run_number)
            max_run = int(options.run_number)
        except ValueError:
            print "Invalid run number = " + options.run_number
            sys.exit(0)

    if options.run_range:
        try:
            (minval,maxval) = options.run_range.split(",")
            min_run = int(minval)
            max_run = int(maxval)
        except:
            print "Invalid run range = " + options.run_range
            sys.exit(0)

    # set statuses
    if options.status_approve:
        status = 1
    if options.status_approve_long:
        status = 2
    if options.status_reject:
        status = 0
    if options.status_unchecked:
        status = -1

    if status is None:
        print "Need to specify status to set!"
        parser.print_help()
        sys.exit(0)

    if max_run is None or min_run is None:
        print "Need to specify runs to set!"
        parser.print_help()
        sys.exit(0)

    # add information to the DB
    db = rcdb.RCDBProvider("mysql://rcdb:%s@gluondb1/rcdb"%options.password)
    if max_run == min_run:
        db.add_condition(max_run, "status", status, True, auto_commit=True)
    else:
        #for run in xrange(min_run,max_run+1):
        query = db.session.query(Run).filter(Run.number.between(min_run,max_run))
        for run in query.all(): 
            db.add_condition(run.number, "status", status, True, auto_commit=False)
        db.session.commit()

## main function 
if __name__ == "__main__":
    main()
