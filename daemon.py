#!/usr/bin/python
# -*- coding: utf-8 -*-
__revision__ = "2015.03.03"
__appname__  = "innmall"
__author__   = "shuxiang29"
__email__    = "shuxiang29@gmail.com"

import re
import threading
import sys, os, time, atexit
try:
    from signal import SIGTERM, SIGKILL
except:
    raise "Current OS doesn't support SIGTERM, SIGKILL."

class Daemon(object):
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        pid_dir = os.path.split(pidfile)[0]
        if not os.path.exists(pid_dir):
            raise Exception("PID directory not exists")

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.timemark = None

    def _daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.setsid()
        os.chdir("/")
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        if self.stdin:
            si = file(self.stdin, 'r')
            os.dup2(si.fileno(), sys.stdin.fileno())
        if self.stdout:
            so = file(self.stdout, 'a+')
            os.dup2(so.fileno(), sys.stdout.fileno())
        if self.stderr:
            se = file(self.stderr, 'a+', 0)
            os.dup2(se.fileno(), sys.stderr.fileno())
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self, timeout=-1):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
            os.kill(pid, 0)
        except IOError:
            pid = None
        except OSError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        self._daemonize()
        self.timemark = time.time()
        if timeout > -1:
            self.monitor(timeout)
        self._run()

    def stop(self):
        """
        Stop the daemon
        """
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
        try:
            while 1:
                #os.kill(pid, SIGTERM)
                os.kill(pid, SIGKILL)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def monitor(self, timeout):
        def check(self, timeout):
            time.sleep(timeout)
            self.stop()
        wather = threading.Thread(target=check)
        wather.setDaemon(True)
        wather.start()

    def _run(self):
        pass

class DaemonHasChildren(Daemon):
    def stop(self):
        pid = None
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pass
        if pid: # kill all child process
            try:
                f = os.popen('ps --ppid=%s'%pid)
                s = f.read()
                for l in s.split('\n'):
                    sid = re.findall(r'\d+', l) # first column is PID
                    if sid:
                        print 'kill', sid[0]
                        os.system('kill %s'%sid[0])
            except:
                print 'Not linux os, can not find the right subprocess.'
        super(DaemonHasChildren, self).stop()

class DaemonWithoutRun(Daemon):
    def start(self):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
            os.kill(pid, 0)
        except IOError:
            pid = None
        except OSError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self._daemonize()
        #self._run()
        #The next is what you want to loop forever, go do it!
