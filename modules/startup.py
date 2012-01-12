#!/usr/bin/env python
"""
startup.py - Phenny Startup Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import threading

def setup(phenny):
   if hasattr(phenny.config, 'refresh_delay'):
      # Ping repeatedly to make sure we're still connected, and if
      # not, disconnect and wait to be restarted.
      refresh_delay=300.0
      try:
         refresh_delay=float(phenny.config.refresh_delay)
      except:
         pass
      
      def pingloop():
         phenny.internals['phennydeath']=threading.Timer(refresh_delay,killme,())
         phenny.internals['phennydeath'].start()
         print "\tsending ping"
         phenny.write(('PING', phenny.config.host))

      phenny.internals['pingloop']=pingloop

      def killme():
         # can we restart from scratch this way?
         print "RESTARTING PHENNY."
         phenny.handle_close()
         # Then the Watcher should restart, yes?

      import time
      def pong(phen, inp):
         print "Been ponged"
         try:
            phenny.internals['phennydeath'].cancel()
            time.sleep(refresh_delay+60.0)
            pingloop()
         except:
            pass
      pong.event='PONG'
      pong.priority='high'
      pong.thread=True
      pong.rule=r'.*'
      phenny.variables['pong']=pong

      # Need to wrap handle_connect to start the loop.
      hc=phenny.handle_connect
      def new_hc():
         hc()
         if hasattr(phenny,'internals') and phenny.internals.get('pingloop'):
            phenny.internals['pingloop']()
      phenny.handle_connect=new_hc


def startup(phenny, input): 
   if hasattr(phenny.config, 'serverpass'): 
      phenny.write(('PASS', phenny.config.serverpass))

   if hasattr(phenny.config, 'password'): 
      phenny.msg('NickServ', 'IDENTIFY %s' % phenny.config.password)
      __import__('time').sleep(5)

   # Cf. http://swhack.com/logs/2005-12-05#T19-32-36
   for channel in phenny.channels: 
      phenny.write(('JOIN', channel))
startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
