# scan logfile to extract information printed to screen during RF calibration

import sys
import re

def get_RF_info(filename):
    # keep results in a hash
    results = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            # check TI-Time uniformity
            matchObj = re.search( r'disagrees with the other ROCs', line, re.M)
            if matchObj:
                if 'TI-TIME' in results.keys():
                    results['TI-TIME'].append(line)
                else:
                    results['TI-TIME'] = [ line ]
            # TODO: check TDC -> time conversion
            # TODO: check RF signal time period
            # TODO: check Beam Bunch Period

    # done
    return results
                
if __name__ == "__main__":
    print str(get_RF_info(sys.argv[1]))
