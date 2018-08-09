#!/bin/tcsh

if ( $1 == "" ) then
    echo "No shell configuration file passed!"
    exit 0
endif

# load environment
source $1

# print svn revision numbers as pseudo env variables
cd $HDDS_HOME
set hdds_ver = `svn info | grep 'Revision' | gawk '{print $2}'`
echo "HDDS_REV=${hdds_ver}"
cd -

cd $HALLD_HOME
set sim_recon_ver = `svn info | grep 'Revision' | gawk '{print $2}'`
echo "SIM_RECON_REV=${sim_recon_ver}"
cd -

# print out the rest of the environment
env
