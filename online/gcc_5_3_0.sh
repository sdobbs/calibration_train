#!/bin/bash

function path_remove {
  # Delete path by parts so we can never accidentally remove sub paths
  PATH=${PATH//":$1:"/":"} # delete any instances in the middle
  PATH=${PATH/#"$1:"/} # delete any instance at the beginning
  PATH=${PATH/%":$1"/} # delete any instance in the at the end
}

function ldlib_path_remove {
  # Delete path by parts so we can never accidentally remove sub paths
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH//":$1:"/":"} # delete any instances in the middle
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH/#"$1:"/} # delete any instance at the beginning
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH/%":$1"/} # delete any instance in the at the end
}



GCC_HOME=/apps/gcc/5.3.0

# Remove all other gcc versions from PATHs
while [ `which gcc` != /usr/bin/gcc ]; do
    loc=`which gcc`
    bindir=`dirname $loc`
    libdir=`dirname $bindir`/lib
    lib64dir=`dirname $bindir`/lib64
    printenv PATH
    path_remove $bindir
    ldlib_path_remove $libdir 
    ldlib_path_remove $lib64dir
    #filter_path PATH $bindir
    #filter_path LD_LIBRARY_PATH $libdir $lib64dir
done

echo "Adding GCC 5.3.0 to PATH"
export PATH=${GCC_HOME}/bin:${PATH}
export LD_LIBRARY_PATH=${GCC_HOME}/lib64:${GCC_HOME}/lib:${LD_LIBRARY_PATH}

# Re-define BMS_OSNAME
#if [ -e ${SETUP_SCRIPTS}/BMS_OSNAME ] source ${SETUP_SCRIPTS}/BMS_OSNAME

GDB_HOME=/gapps/gdb/${BMS_OSNAME}/7.11/
if [ ! -e $GDB_HOME ]; then
    echo "Cannot setup GDB 7.11 (can't find "${GDB_HOME}")"
    echo "Defaulting to system debugger which probably won't"
    echo "be able to read any symbols."
else
     echo "Adding GDB 7.11 to PATH"
     export PATH=${GDB_HOME}/bin:${PATH}
     export LD_LIBRARY_PATH=${GDB_HOME}/lib:${LD_LIBRARY_PATH}
fi

# Use filter_path from ../setup_init.csh to compact things
#filter_path PATH
#filter_path LD_LIBRARY_PATH
export PATH
export LD_LIBRARY_PATH

