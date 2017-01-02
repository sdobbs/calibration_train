import os

with open("run_lists/f16_runs.all", "r") as f:
    for line in f:
        run = int(line.strip())
        os.system("python HDSubmitCalibJobSWIF.py configs/data.config 2016-10 pass1 %d 1"%run)
