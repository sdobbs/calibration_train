#!/bin/bash
# modified from /etc/gluex/hdonline.cshrc

source gcc_4_9_2.sh

#export LD_LIBRARY_PATH=""
export JANA_PLUGIN_PATH=""
#export PYTHONPATH=""
export BMS_OSNAME=`/gluex/sim-recon/scripts/osrelease.pl`

export HTTPS_PROXY=https://jprox:8082
export HTTP_PROXY=http://jprox:8082

# sim-recon (sets up ROOT, XERCES, HDDS, JANA and CCDB)
source /gluex/sim-recon/sim-recon/${BMS_OSNAME}/setenv.sh

# Select one of the following
#export CCDB_CONNECTION mysql://ccdb_user@gluondb1.jlab.org/ccdb
export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb
export JANA_CALIB_URL=${CCDB_CONNECTION}
export JANA_RESOURCE_DIR=/gluex/sim-recon/resources

export HALLD_HOME=/gluonwork1/Users/sdobbs/Software/halld_recon
export PATH=$HALLD_ONLINE_RELEASE/${BMS_OSNAME}/bin:${PATH}
export LD_LIBRARY_PATH=$HALLD_ONLINE_RELEASE/${BMS_OSNAME}/lib:${LD_LIBRARY_PATH}
export JANA_PLUGIN_PATH=$HALLD_ONLINE_RELEASE/${BMS_OSNAME}/plugins:${JANA_PLUGIN_PATH}
export JANA_GEOMETRY_URL=ccdb:///GEOMETRY/main_HDDS.xml

# setup pyROOT
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH

# PYTHON 2.7 for CCDB
#export PATH /apps/python/PRO/bin:$PATH
#export LD_LIBRARY_PATH /apps/python/PRO/lib:$LD_LIBRARY_PATH
export PATH=/apps/python/python-2.7.1/bin:$PATH
export LD_LIBRARY_PATH=/apps/python/python-2.7.1/lib:$LD_LIBRARY_PATH
export CCDB_USER=hdsys

# RCDB
source /gluonwork1/Users/sdobbs/Software/rcdb/environment.bash

# use the good git
export PATH=/apps/bin:$PATH

# JOB CONFIGURATION
export NTHREADS=30