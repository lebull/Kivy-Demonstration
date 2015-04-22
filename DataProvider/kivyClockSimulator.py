import logging

import threading
import time
from kivy.clock import Clock


class ClockSim(threading.Thread):
    """
    A helper class for testing.
    
    Since Kivy is built to be asynchronous, we need to have kivy's
    internal clock ticking."""
    
    def __init__(self, **kwargs):       
        self._run_clock = False     
        self._debug = False
        super(ClockSim, self).__init__(**kwargs)
        
        
    def run(self, *args):
        
        logging.info("Clock Simulator Started")
        
        if(self._run_clock == False):
            self._run_clock = True
            
        if self._debug: Clock.schedule_interval(self._printTick, 1)
        
        while (self._run_clock):                                
            Clock.tick()
            time.sleep(0.1)
                
    def stop(self):
        '''Stop the clock simulator thread.
        '''
        
        logging.info("Clock Simulator Stopped")
        self._run_clock = False
        self.join()
        
    def _printTick(self, dt):
        print "ClockSim Says: Tick"

