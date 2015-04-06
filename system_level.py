
'''
/*
*
*
* Copyright (C) 2015 Yeshwanth Kumar <morpheyesh@gmail.com>
*
*
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License
* as published by the Free Software Foundation; either version 2
* of the License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, see <http://www.gnu.org/licenses/>.
*/

'''

import os
import re
import string
import subprocess
import platform
import sys
import httplib, urllib
import time


import pika
import json
import urllib2

from hashlib import md5
current_python = platform.python_version_tuple()

headers = { #not required. design changed- using AMQP
    'User-Agent': 'DataDust Agent',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html, */*',
}
class system_level:

 def __init__(self, ddConfig): #Explicit is better than implicit
   self.ddConfig = ddConfig
   print "Done Init-ing!"



 def Disk_Util(self):
   disk_usage = []
   try:
     proc = subprocess.Popen(['df','-k'],stdout=subprocess.PIPE, shell=True)
     print proc
     command_exec = proc.communicate()[0]
     print command_exec


   except:
      print "Error! Cannot run commands"

   into_tuple = command_exec.split('\n')
   into_tuple.pop(0)

   for singleStat in into_tuple:

        singleStat = singleStat.split()

        disk_usage.append(singleStat)

   return disk_usage

 def CPU_Stats(self):

    stats = {}

    if sys.platform == 'linux2':
       print "Good to go!"

       itemR= re.compile(r'.*?\s+(\d+)[\s+]?')
       valueR = re.compile(r'\d+\.\d+')
       headR = re.compile(r'.*?([%][a-zA-Z0-9]+)[\s+]?')
       proc = None

       try:
          proc = subprocess.Popen(['mpstat', '-P', 'ALL', '1', '2'], stdout=subprocess.PIPE, shell=True)

          mpstat = proc.communicate()[0]
          print "----"
          print mpstat
          if int(current_python[1]) >= 6:
              try:
                  proc.kill()
              except:
                  print "proc is dead already! "

              mpstat = mpstat.split('\n')
              mpstat.pop(1)
              head = mpstat[1]
              headName = re.findall(headR, head)

              #take each line out

              for singleLine in range (2, len(mpstat)):
                  singleIndex =  mpstat[singleLine]

                  if not singleIndex:
                      break

                  device = re.match(itemR, singleIndex)

                  if string.find(singleIndex, 'all') is not -1:
                      ndevice = 'ALL'
                  elif device is not None:
                      ndevice = 'CPU%s' % device.groups()[0]

                  values = re.findall(valueR, singleIndex.replace(',','.'))

                  stats[ndevice] = {}

                  for headerIndex in range(0, len(headName)):
                      headNames = headName[headerIndex]
                      stats[ndevice][headNames] = values[headerIndex]


       except OSError:
          return false

    else:
        print 'Different platform!'
        return False

    print 'Done!'
    print stats
    return stats

 def freeMemory(self):

     if sys.platform == 'linux2':
         print ("alrighty!")

         try:
           free_mem = subprocess.Popen(['free mem'], stdout=subprocess.PIPE, shell=True)
           freemem = free_mem.communicate()[0]

           singleTuples =  freemem.split('\n')

           split_them = singleTuples[1].split()

           total = split_them[1]
           used = split_them[2]
           free = split_them[3]
           #convert to Gbs
           totalMemory = (float(total) / 1024) / 1024
           usedMemory = (float(used) / 1024 ) / 1024
           freeMemory = (float(free) / 1024) / 1024
           #print totalMemory
           #print userMemory
           #print freeMemory

           freeMemory = {
                   'total': totalMemory,
                   'usedMemory': usedMemory,
                   'freeMemory': freeMemory
                         }
           print freeMemory
           return freeMemory





         except:
            print ("subprocess did not execute")

     else:
         print ("It does not work at all")

#network monitoring

#--taking it from /proc/net/dev - need to find out what all and how all data can be taken from the procs
#efficiently. Also need to test the memory usage of the daemon(.)



def NetworkTraffic(self):
    if sys.platform == 'linux2':
        try:
            procdata = open('/proc/net/dev', 'r')
            allLines = procdata.readlines()
            procdata.close()

        except:
            print ("Error - ")
            return false

        _,first,second = allLines.split('|')
        full = first + second

        indexDict = {}

        for line in allLines[2:]:
            if line.find(':') < 0:
                continue
        index, data = line.split(':')
        fullData = dict(zip(full, data.split()))
        indexDict[index] = fullData

    return indexDict
    
 def PostBack(self, Data):

    connection = pika.BlockingConnection(pika.ConnectionParameters(
                    'localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=os.uname()[1])
    channel.basic_publish(exchange='',
                      routing_key=os.uname()[1],
                      body=Data)
    connection.close()




 def system_levelChecks(self, schedule, booly, BasicStats=False):
        pData = {}
        global pData
        os =  platform.dist()

        diskUtil = self.Disk_Util()
        cpuStats = self.CPU_Stats()

        timestamp = time.strftime("%d/%m/%y") + ' ' + time.strftime("%H:%M:%S")

        #payload
        finalPayload = {
                'os': os
                      }
        if timestamp:
            finalPayload['timestamp'] = timestamp
        if cpuStats:
            finalPayload['cpuStats'] = cpuStats
        if diskUtil:
            finalPayload['diskUtil'] = diskUtil


        if booly:
            finalPayload['BasicStats'] = BasicStats


        pyV = platform.python_version_tuple()

        #now convert the data into JSON
        if int(pyV[1]) >= 6:

            try:
                JsonData = json.dumps(finalPayload, encoding='latin1').encode('utf-8')


            except Exception:
                print("Nah! Not happening!")
                return false

        else:
            #need to use minjson and support py V2.5 and below...(.)
            print("ahh! the py is old!")
        '''
        pHash = md5(JsonData).hexdigest()
        #global pData
        pData = urllib.urlencode (   #?
            {
             'payload': JsonData,
              'hash': pHash
                }
            )
        print pData
        '''

        self.PostBack(JsonData)
        #DONE

        schedule.enter(self.ddConfig['interval'], 1, self.system_levelChecks, (schedule, False))
