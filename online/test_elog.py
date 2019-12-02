
import sys
import os
#sys.path.append('../../lib/' + os.environ.get("HOST_ARCH"))
sys.path.append('/site/ace/cebaf/certified/apps/eloglib/2.0.1/swig/php/lib/rhel-6-ia32')
import eloglib
import datetime

log = eloglib.Logentry('eloglib test', 'TLOG')
#admin = eloglib.LogentryAdminExtension(log)
log.setBody('Hello <b>world</b>', eloglib.LogItem.C_html)
#log.addLogbooks('TLOG')
#log.addTags('Readme,Target')
#log.addReference('atlis', 5)
log.setEmailNotify('sdobbs@jlab.org')
#admin.setCreated(946702800)
#log.setSticky(1)
print log.getXML()
