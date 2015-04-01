import logging

import threading
import time
from kivy.clock import Clock


class ClockSim(threading.Thread):
    """
    A helper class for testing.
    
    Since Kivy is built to be asynchronous, we need to have kivy's
    internal clock ticking."""
    
    def __init__(self, network_providers = [], stop_when_requests_done = True, **kwargs):
        """
        @param network_providers
        @type list of NetworkProviders
        
        @param stop_when_requests_done
        @type boolean
        """
        self._run_clock = False
        self.network_providers = network_providers
        self.stop_when_requests_done = stop_when_requests_done
        
        super(ClockSim, self).__init__(*kwargs)
        
    def run(self, *args):
        while (self._run_clock):

            if(self.stop_when_requests_done
               and len(self.network_providers)
               and self.checkRequestsRemain() == False):
                self.stop()
                logging.info("All requests complete.  Stopping Kivy clock simulation.")
                                
            Clock.tick()
            time.sleep(0.1)
                
    def checkRequestsRemain(self):
        """Check to see if there are any pending requests 
        in the monitored NetworkDataProviders."""
        for provider in self.network_providers:
            if provider.pending_requests > 0:
                return True
            
        return False
        
    def start(self, **kwargs):
        """Spawn a clock-ticking thread.  Make sure to call
        stop() when you are done with it."""
        
        if(self._run_clock == False):
            self._run_clock = True
            super(ClockSim, self).start(**kwargs)

        
    def stop(self):
        """Stop the clock simulator"""
        self._run_clock = False

