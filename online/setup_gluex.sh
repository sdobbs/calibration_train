#!/bin/bash
# modified from /etc/gluex/hdonline.cshrc

#source gcc_4_9_2.sh
#export LD_LIBRARY_PATH=""
export JANA_PLUGIN_PATH=""
#export PYTHONPATH=""
export BMS_OSNAME=`/gluex/sim-recon/scripts/osrelease.pl`

export HTTPS_PROXY=https://jprox:8082
export HTTP_PROXY=http://jprox:8082

# support the latest compiler used by the gluons
export LD_LIBRARY_PATH=/apps/gcc/5.3.0/lib64:/apps/gcc/5.3.0/lib:$LD_LIBRARY_PATH

# setup GlueX software
export BUILD_SCRIPTS=/gluonfs1/home/sdobbs/work/Software/build_scripts
export BMS_OSNAME=`$BUILD_SCRIPTS/osrelease.pl`

source /gluex/builds/${BMS_OSNAME}/halld_recon/halld_recon-latest/${BMS_OSNAME}/setenv.sh

# my recon
export HALLD_RECON_HOME=/gluonwork1/Users/sdobbs/Software/halld_recon
export PATH=$HALLD_RECON_HOME/${BMS_OSNAME}/bin:${PATH}
export LD_LIBRARY_PATH=$HALLD_RECON_HOME/${BMS_OSNAME}/lib:${LD_LIBRARY_PATH}
export JANA_PLUGIN_PATH=$HALLD_RECON_HOME/${BMS_OSNAME}/plugins:${JANA_PLUGIN_PATH}

# my sim 
export HALLD_SIM_HOME=/gluonwork1/Users/sdobbs/Software/halld_sim
export PATH=$HALLD_SIM_HOME/${BMS_OSNAME}/bin:${PATH}
export LD_LIBRARY_PATH=$HALLD_SIM_HOME/${BMS_OSNAME}/lib:${LD_LIBRARY_PATH}
export JANA_PLUGIN_PATH=$HALLD_SIM_HOME/${BMS_OSNAME}/plugins:${JANA_PLUGIN_PATH}

# Select one of the following
export CCDB_CONNECTION=mysql://ccdb_user@gluondb1.jlab.org/ccdb
#export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb
export JANA_CALIB_URL=${CCDB_CONNECTION}
export JANA_RESOURCE_DIR=/gluex/sim-recon/resources
export JANA_GEOMETRY_URL=ccdb:///GEOMETRY/main_HDDS.xml

# setup pyROOT
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH

# PYTHON 2.7 for CCDB
#export PATH /apps/python/PRO/bin:$PATH
#export LD_LIBRARY_PATH /apps/python/PRO/lib:$LD_LIBRARY_PATH
export PATH=/apps/python/python-2.7.1/bin:$PATH
export LD_LIBRARY_PATH=/apps/python/python-2.7.1/lib:$LD_LIBRARY_PATH
#export PYTHONPATH=$CCDB_HOME/python:$PYTHONPATH
export CCDB_USER=hdsys

# RCDB
source /gluonwork1/Users/sdobbs/Software/rcdb/environment.bash

# use the good git
export PATH=/apps/bin:$PATH

# JOB CONFIGURATION
export NTHREADS=30
