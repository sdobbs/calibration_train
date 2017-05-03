import rcdb

db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb")
#runs = db.select_runs("@is_production", 10000, 20000)
#runs = db.select_runs("@is_production", 10530, 20000)
#runs = db.select_runs("@is_production and @status_approved", 11313, 20000)
runs = db.select_runs("@is_production and @status_approved", 30000, 39999)

for run in runs:
    print run.number
