import os
import sys

process_id = str(os.getpid())
pidfile = "/tmp/whet.pid"

class Pid(object):
    """ Class to cread a process id file to stop multiple copies running"""
    def __init__(self):
        #PID CHECK
        if os.path.isfile(pidfile):
            print "%s already exists, exiting" % pidfile
            sys.exit()
        file(pidfile, 'w').write(process_id)

    def kill(self):
        """ Deletes the pid, call when shutdown safely """
        os.unlink(pidfile)
