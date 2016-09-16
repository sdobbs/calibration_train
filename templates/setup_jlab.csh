###############################################################
#
# 2014/12/09 Kei Moriya
#
# This file was copied and modified from the file alias
# /home/gluex/setup_jlab_commissioning.csh
#
# Changes from original are:
# - HALLD_HOME, HDDS_HOME, CCDB_HOME, JANA_HOME are local builds.
# - JANA_CALIB_URL is set to ${GLUEX_TOP}/ccdb.sqlite, which
#    should be created for each launch
# - JANA_PLUGIN_PATH is set to reflect this build.
#
###############################################################

# Set versions of software to use here, they will
# be used to modify PATH and LD_LIBRARY_PATH when
# $BUILD_SCRIPTS/gluex_env.csh is sourced.
#
#module load gcc_4.9.2


# SET /apps/bin AT FRONT OF PATH (to use working version of git)
setenv PATH /apps/bin:$PATH

# SETUP gcc 4.9.2
setenv PATH /apps/gcc/4.9.2/bin:${PATH}
if (! $?MANPATH) then
        setenv MANPATH
endif
setenv MANPATH /apps/gcc/4.9.2/share/man:${MANPATH}
if (! $?LD_LIBRARY_PATH) then
        setenv LD_LIBRARY_PATH
endif
setenv LD_LIBRARY_PATH /apps/gcc/4.9.2/lib64:/apps/gcc/4.9.2/lib:${LD_LIBRARY_PATH}

# Use common build for these
setenv BUILD_SCRIPTS /group/halld/Software/build_scripts
setenv BMS_OSNAME `$BUILD_SCRIPTS/osrelease.pl`
#setenv ROOTSYS     /group/halld/Software/builds/$BMS_OSNAME/root/root_5.34.34
setenv ROOTSYS     /group/halld/Software/builds/Linux_CentOS6-x86_64-gcc4.9.2/root/root_6.06.04
setenv EVIOROOT    /group/halld/Software/builds/$BMS_OSNAME/evio/evio-4.3.1/Linux-x86_64
setenv XERCESCROOT /group/halld/Software/builds/$BMS_OSNAME/xerces-c/xerces-c-3.1.2

# `$BUILD_SCRIPTS/cue_root.pl`
#setenv CERN_CUE `$BUILD_SCRIPTS/cue_cernlib.pl`
#setenv CERN `$BUILD_SCRIPTS/cue_cernlib.pl`
setenv CERN /group/halld/Software/builds/Linux_CentOS6-x86_64-gcc4.9.2/cernlib
setenv CERN_CUE /group/halld/Software/builds/Linux_CentOS6-x86_64-gcc4.9.2/cernlib
setenv CERN_LEVEL 2005

# We will have our own versions of
# - sim-recon
# - hdds
# - ccdb
# - jana

# Top level directory
setenv GLUEX_TOP /work/halld2/home/gxproj3/Calibration/Software/

setenv HALLD_HOME  ${GLUEX_TOP}/sim-recon/sim-recon
setenv HDDS_HOME   ${GLUEX_TOP}/hdds/hdds
# CCDB must be built before JANA
# To get CCDB via svn, use
# svn co https://phys12svn.jlab.org/repos/trunk/ccdb
#setenv CCDB_HOME   ${GLUEX_TOP}/ccdb/ccdb_1.05
#setenv CCDB_HOME   ${GLUEX_TOP}/ccdb/ccdb.git
#setenv JANA_HOME   ${GLUEX_TOP}/jana/jana_0.7.5p2/$BMS_OSNAME

setenv RCDB_HOME  /group/halld/Software/builds/$BMS_OSNAME/rcdb/rcdb_0.00
setenv CCDB_HOME  /group/halld/Software/builds/$BMS_OSNAME/ccdb/ccdb_1.06.01
#setenv JANA_HOME  /group/halld/Software/builds/$BMS_OSNAME/jana/jana_0.7.5p2/$BMS_O
setenv JANA_HOME /group/halld/Software/builds/$BMS_OSNAME/jana/jana_0.7.5p2^root6/$BMS_OSNAME/

#------------------------------------------------------------#
#                Check that all directories exist            #
#------------------------------------------------------------#
if ( ! (-e $GLUEX_TOP) ) then
  echo "---setup_jlab.csh:   Variable GLUEX_TOP could not be set to"
  echo "---setup_jlab.csh:   $GLUEX_TOP (does not exist)"
  echo "---setup_jlab.csh:   aborting..."
  exit
endif

if ( ! (-e $HALLD_HOME) ) then
  echo "---setup_jlab.csh:   Variable HALLD_HOME could not be set to"
  echo "---setup_jlab.csh:   $HALLD_HOME (does not exist)"
  echo "---setup_jlab.csh:   aborting..."
  exit
endif

if ( ! (-e $HDDS_HOME) ) then
  echo "---setup_jlab.csh:   Variable HDDS_HOME could not be set to"
  echo "---setup_jlab.csh:   $HDDS_HOME (does not exist)"
  echo "---setup_jlab.csh:   aborting..."
  exit
endif

if ( ! (-e $CCDB_HOME) ) then
  echo "---setup_jlab.csh:   Variable CCDB_HOME could not be set to"
  echo "---setup_jlab.csh:   $CCDB_HOME (does not exist)"
  echo "---setup_jlab.csh:   aborting..."
  exit
endif

if ( ! (-e $JANA_HOME) ) then
  echo "---setup_jlab.csh:   Variable JANA_HOME could not be set to"
  echo "---setup_jlab.csh:   $JANA_HOME (does not exist)"
  echo "---setup_jlab.csh:   aborting..."
  exit
endif

# -----------------------------------------------------------------
# THIS SCRIPT WILL ADD MODIFY PATH AND LD_LIBRARY_PATH TO INCLUDE
#  ENVIRONMENT VARIABLES SET ABOVE
source $BUILD_SCRIPTS/gluex_env.csh
# -----------------------------------------------------------------

# configure ROOT python bindings
setenv PYTHONPATH $ROOTSYS/lib:$PYTHONPATH
setenv PYTHONPATH $HALLD_HOME/$BMS_OSNAME/lib:$PYTHONPATH
# python for sim-recon
setenv PYTHONPATH $HALLD_HOME/$BMS_OSNAME/python2:$PYTHONPATH
# Add 
# setenv LD_LIBRARY_PATH $EVIOROOT/lib:$LD_LIBRARY_PATH

# make sure to set the correct calibtime - FIX
#setenv JANA_CALIB_URL  sqlite:///${GLUEX_TOP}/ccdb.sqlite # mysql://ccdb_user@hallddb.jlab.org/ccdb
#setenv CCDB_CONNECTION sqlite:///${GLUEX_TOP}/ccdb.sqlite # mysql://ccdb_user@hallddb.jlab.org/ccdb
# /group/halld/www/halldweb/html/dist/ccdb.sqlite
# setenv JANA_CALIB_CONTEXT "calibtime=2015-02-11T00:00"
setenv JANA_RESOURCE_DIR /group/halld/www/halldweb/html/resources

if ( ! $?JANA_PLUGIN_PATH ) then
  setenv JANA_PLUGIN_PATH 
endif
setenv JANA_PLUGIN_PATH ${HALLD_HOME}/${BMS_OSNAME}/plugins\:${JANA_HOME}/plugins:${JANA_PLUGIN_PATH}

# python2.7 needed for CCDB command line tool
setenv PATH /apps/python/PRO/bin\:$PATH
setenv LD_LIBRARY_PATH /apps/python/PRO/lib\:$LD_LIBRARY_PATH

#------------------------------------------------------------#
#              Print out environment variables               #
#------------------------------------------------------------#

#echo "GlueX Environment"
#echo ""
#echo "GLUEX_TOP           :    $GLUEX_TOP"
#echo "HALLD_HOME          :    $HALLD_HOME"
#echo "CCDB_HOME           :    $CCDB_HOME"
#echo "JANA_HOME           :    $JANA_HOME"
#echo "JANA_CALIB_URL      :    $JANA_CALIB_URL"
#echo "CCDB_CONNECTION     :    $CCDB_CONNECTION"
#echo "JANA_RESOURCE_DIR   :    $JANA_RESOURCE_DIR"
#echo "JANA_PLUGIN_PATH    :    $JANA_PLUGIN_PATH"
#echo "PATH                :    $PATH"
#echo "LD_LIBRARY_PATH     :    $LD_LIBRARY_PATH"

