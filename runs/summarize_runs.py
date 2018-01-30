import rcdb
import sys

db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb")
runs = db.select_runs("@is_production and @status_approved", sys.argv[1], sys.argv[2])

num_trig = 0
num_trig_para = 0
num_trig_perp = 0
for run in runs:
    nevts = int(db.get_condition(run.number, "event_count").value)
    pol = db.get_condition(run.number, "polarization_direction").value
    num_trig += nevts
    if pol == "PARA":
        num_trig_para += nevts
    if pol == "PERP":
        num_trig_perp += nevts

print "total triggers = " + str(num_trig)
print "total PARA triggers = " + str(num_trig_para)
print "total PERP triggers = " + str(num_trig_perp)
print "total AMO triggers  = " + str(num_trig-num_trig_para-num_trig_perp)
