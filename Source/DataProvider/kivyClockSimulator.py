import logging

import threading
import time
from kivy.clock import Clock


class KivyClockSimulator(threading.Thread):
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
    
        self.callbacks = []
        
        super(KivyClockSimulator, self).__init__(*kwargs)
        
    def run(self, *args):
        while (self._run_clock):
                
                if(self.stop_when_requests_done 
                   and self.checkRequestsRemain() == False):
                    self.stopMainLoopSimulation()
                    logging.info("All requests complete.  Stopping Kivy clock simulation.")
                    
                for f in self.callbacks:
                    f()
                    
                Clock.tick()
                time.sleep(0.1)
                
    def checkRequestsRemain(self):
        for provider in self.network_providers:
            if provider.pending_requests > 0:
                return True
            
        return False
        
    def startMainLoopSimulation(self):
        """Spawn a clock-ticking thread.  Make sure to call
        stopKivyMainLoopSimulation() when you are done with it.

        This is probably a horrible idea"""
        self._run_clock = True
        self.start()

    def stopMainLoopSimulation(self):
        self._run_clock = False
        
    def addCallback(self, function):
        self.callbacks.append(function)
