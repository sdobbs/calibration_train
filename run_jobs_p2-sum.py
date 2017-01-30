import os

with open("run_lists/f16_runs.all.good", "r") as f:
    for line in f:
        run = int(line.strip())
        os.system("python HDSubmitCalibJobSWIF.py configs/data.config.sum 2016-10 pass2-sum %d"%run)
