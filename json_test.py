import json
import os,sys
import subprocess

# "swif status -workflow GlueX-CalibRun-2016-01-22 -display json"

p = subprocess.Popen("swif status -workflow GlueX-CalibRun-2016-04-27 -display json",stdout=subprocess.PIPE,shell=True)
(stdout,stderr) = p.communicate()
workflow_info_json = json.loads(stdout)

workflow_info = {}
for i in xrange(len(workflow_info_json["columns"])):
    workflow_info[ workflow_info_json["columns"][i] ] =  workflow_info_json["rows"][0][i]

print str(workflow_info)
print ""
print "phase = " + str(workflow_info["phase"])
