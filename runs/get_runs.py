import rcdb

db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb")
#runs = db.select_runs("@is_2018production", 40000, 50000)
#runs = db.select_runs("@is_2018production and status!=0 and polarimeter_converter=='Be 750um'", 40000, 50000)
#runs = db.select_runs("@is_2018production and @status_approved", 40000, 41100)
#runs = db.select_runs("@is_2018production and @status_approved", 41000, 41200)
runs = db.select_runs("@is_2018production and @status_approved", 41200, 41600)
#runs = db.select_runs("@is_2018production and status!=0", 40000, 50000)
#runs = db.select_runs("@is_2018production and status!=0", 40653, 40852)
#runs = db.select_runs("@is_2018production and status!=0", 41632, 50000)
#runs = db.select_runs("@is_2018production and status!=0", 42158, 50000)
#runs = db.select_runs("@is_2018production and status!=0", 42188, 50000)
#runs = db.select_runs("@is_2018production and status!=0", 41978, 50000)
#runs = db.select_runs("@is_2018production and status!=0", 041100, 50000)
#runs = db.select_runs("@is_production", 10000, 20000)
#runs = db.select_runs("@is_production", 10530, 20000)
#runs = db.select_runs("@is_production and @status_approved", 11313, 20000)
#runs = db.select_runs("@is_production and @status_approved", 11299, 20000)
#runs = db.select_runs("@is_production and @status_approved", 30000, 40000)
#runs = db.select_runs("@status_approved", 30000, 40000)
#runs = db.select_runs("status==1 or status==3", 40000, 50000)

for run in runs:
    print run.number
