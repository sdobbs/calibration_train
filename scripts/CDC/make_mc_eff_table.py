import os,sys

bad_straws = []

# read list in 
if len(sys.argv)>1:
    with open(sys.argv[1]) as f:
        for line in f:
            if line[0] == '#':
                continue
            try:
                bad_straws.append( int(line.strip()) )
            except:
                continue



# build CCDB table
for x in range(1,3523):
    if x in bad_straws:
        print "0"
    else:
        print "1"
