import rcdb

db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb")
#runs = db.select_runs("@is_production", 10000, 20000)
#runs = db.select_runs("@is_production", 10530, 20000)
#runs = db.select_runs("@is_production and @status_approved", 11313, 20000)
#runs = db.select_runs("@is_production and @status_approved", 11299, 20000)
#runs = db.select_runs("@is_production and @status_approved", 30000, 40000)
#runs = db.select_runs("@status_approved", 30000, 40000)
runs = db.select_runs("status==1 or status==3", 40000, 50000)

for run in runs:
    print run.number
