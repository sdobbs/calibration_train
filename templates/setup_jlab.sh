#!/bin/bash

# ALTERNATIVE HOME FOLDER
export HALLD_MY=/home/gxproj3/halld_my

# SET PATH FOR PERL MODULES (Does not seem to be automatically present when running jobs from cron)
#export PERL5LIB=/usr/local/lib64/perl5:/usr/local/share/perl5:/usr/lib64/perl5/vendor_perl:/usr/share/perl5/vendor_perl:/usr/lib64/perl5:/usr/share/perl5

# SET SOFTWARE VERSIONS/PATHS (e.g. $ROOTSYS, $CCDB_HOME, etc.)
export GLUEX_VERSION_XML=version_calib.xml

# SET FULL ENVIRONMENT
export EDITOR=nano
export BUILD_SCRIPTS=/group/halld/Software/build_scripts/
source $BUILD_SCRIPTS/gluex_env_jlab.sh $GLUEX_VERSION_XML

export JANA_RESOURCE_DIR=/group/halld/www/halldweb/html/resources

# quick fix for rootcling compilation
unset CPLUS_INCLUDE_PATH

# configure ROOT python bindings
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH
export PYTHONPATH=$HALLD_HOME/$BMS_OSNAME/lib:$PYTHONPATH
# python for sim-recon
export PYTHONPATH=$HALLD_HOME/$BMS_OSNAME/python2:$PYTHONPATH

# python2.7 needed for CCDB command line tool - this is the version needed for the CentOS7 nodes
export PATH=/apps/python/2.7.12/bin:$PATH
export LD_LIBRARY_PATH=/apps/python/2.7.12/lib:$LD_LIBRARY_PATH
