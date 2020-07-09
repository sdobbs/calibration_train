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
#setup gcc5.3.0
source gcc_5_3_0.sh
export LD_LIBRARY_PATH=/apps/gcc/5.3.0/lib64:/apps/gcc/5.3.0/lib:$LD_LIBRARY_PATH

# Python
#setup python2.7.11
source python_2_7_11.sh
set PYEPICS_ROOT=/gapps/pyepics/pyepics-3.2.1/lib/python2.7/site-packages
#PYEPICS_ROOT=/home/sdobbs/python/pyepics-3.4.1/lib/python3.4/site-packages

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

# EPICS
#export PYTHONPATH=/gapps/pyepics/pyepics-3.2.1/lib/python2.7/site-packages:$PYTHONPATH
#export LD_LIBRARY_PATH=/gluex/controls/epics/R3-14-12-4-RHEL7/extensions/lib/linux-x86_64:/gluex/controls/epics/R3-14-12-4-RHEL7/base/lib/linux-x86_64:/usr/local/lib:/gapps/python/2.7.11/lib:/apps/gcc/5.3.0/lib64:/apps/gcc/5.3.0/lib:/gluex/controls/epics/R3-14-12-4-RHEL7/app/lib/linux-x86_64:/gluex/controls/epics/R3-14-12-4-RHEL7/drivers/lib/linux-x86_64:$LD_LIBRARY_PATH

export PYEPICS_ROOT=/gapps/pyepics/pyepics-3.2.1/lib/python2.7/site-packages

# Set environment for EPICS base and Hall D EPICS builds
if [ ${BMS_OSNAME} == 'Linux_CentOS5-i686-gcc4.1.2' ]; then
# Different EPICS for RHEL5
    source /gluonwork1/Users/sdobbs/calibration_train/online/epicsrc 3-14-12-3-RHEL5
elif [ ${BMS_OSNAME} == 'Linux_RHEL7-x86_64-gcc4.8.5' ]; then
# This is for RHEL7 hosts while it is not the default Linux version for us
    source /gluonwork1/Users/sdobbs/calibration_train/online/epicsrc 3-14-12-4-RHEL7
elif [ ${BMS_OSNAME} == 'Linux_RHEL7-x86_64-gcc5.3.0' ]; then
    source /gluonwork1/Users/sdobbs/calibration_train/online/epicsrc 3-14-12-4-RHEL7
else
# This is for the default EPICS base version which should be used
# for most of the cases.
    source /gluonwork1/Users/sdobbs/calibration_train/online/epicsrc 3-14-12-4-RHEL7
fi

# Add extensions directory to LD_LIBRARY_PATH
# (this should probably be done in /gluex/controls/epics/.epicsrc)
#setenv LD_LIBRARY_PATH  "${LD_LIBRARY_PATH}:${EPICS_EXTENSIONS}/lib/${EPICS_HOST_ARCH}"

# Set environment for PyEPICS  (setting PYEPICS_LIBCA is
# required since 32bit EPICS is first in LD_LIBRARY_PATH)
export PYEPICS_LIBCA=${EPICS_BASE}/lib/linux-`uname -p`/libca.so
export PYTHONPATH=${PYEPICS_ROOT}:${PYTHONPATH}

