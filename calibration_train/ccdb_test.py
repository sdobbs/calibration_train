import HDCCDBCopier

ccdb_file = "sqlite:////u/scratch/gxproj3/ccdb.sqlite"

copier = HDCCDBCopier.HDCCDBCopier(ccdb_file,run=0,variation="calib")
copier.CopyTable("/CDC/base_time_offset",dest_minrun=3180,dest_variation="calib_pass0")
