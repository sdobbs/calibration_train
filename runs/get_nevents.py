import rcdb

db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb")
runs = db.select_runs("event_count > 100", 10000, 20000)
#runs = db.select_runs("@status_approved", 11313, 20000)

total = 0
for run in runs:
    nevts = db.get_condition(run.number, "event_count").value
    print str(run.number) + " " + str(nevts)
    total += nevts

print "TOTAL = " + str(total)
    
