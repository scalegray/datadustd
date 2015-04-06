'''



 Copyright (C) 2015 Yeshwanth Kumar <morpheyesh@gmail.com>


 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, see <http://www.gnu.org/licenses/>.

'''

#!/usr/bin/env python


import sys
import subprocess
import platform
import sched
import time
import os

from system_level import system_level
from ddDaemon import Daemon

if (sys.version_info[1]) <= 6:
    print("Its recommended to use python version 2.7 or above. 2.7 is the best!")
    sys.exit(1)

ddConfig = {
        'version': '0.1.0',
        'interval': 5
           }

def no_of_cores():

    greppy = subprocess.Popen(['grep', 'cpu cores', '/proc/cpuinfo'], stdout=subprocess.PIPE, close_fds = True, shell = True)
    printLine = subprocess.Popen(['wc -l'], stdin=greppy.stdout, stdout=subprocess.PIPE, close_fds = True, shell = True)
    noOfCores = printLine.communicate()[0]

    return int(noOfCores)

class datadust_agent(Daemon):



 #def run(self):
    BasicStats = {
            'processorType': platform.processor(),
            'noOfCores': no_of_cores(),
            'os': sys.platform,
            'nixDist': platform.dist(),
            'hostname' :  os.uname()[1]
                 }
    #expand later when more dist support!(.)


    #system_level instance
    sysLevel = system_level(ddConfig)
    schedule = sched.scheduler(time.time, time.sleep)
    sysLevel.system_levelChecks(schedule, True, BasicStats)
    schedule.run()


if __name__ == '__main__':
      argL = len(sys.argv)
    #need to do logging - logFile(.)

      ddConfig['pidfileDirectory'] = '/tmp/'
      pidFile = None
      if argL == 3 or argL == 4:
        if sys.argv[2] == 'init':

            if os.path.exists('/var/run/datadust-agent/'):
                pidFile = '/var/run/datadust-agent/datadust-agent.pid'
            else:
                pidFile = '/var/run/datadust-agent.pid'

      else:
         pidFile = os.path.join(ddConfig['pidfileDirectory'], 'datadust-agent.pid')


      if not os.access(ddConfig['pidfileDirectory'], os.W_OK):
       print 'Unable to write the PID file at ' + pidFile
       print 'Agent will now quit'
       sys.exit(1)

      d = datadust_agent(pidFile) #pids..(..)

      if argL == 2 or argL == 3 or argL == 4:
         if 'start' == sys.argv[1]:
            print("Started daemon-->")
            d.start()

         elif 'stop' == sys.argv[1]:
             print("Daemon stopped!")
             d.stop()




         else:
            print 'Check the commands properly!'
            sys.exit(1)

         sys.exit(0)

      else:
        print 'usage: %s start|stop|restart|status|update' % sys.argv[0]
        sys.exit(1)
