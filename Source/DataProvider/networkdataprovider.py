'''
Created on Mar 26, 2015

@author: TDARSEY
'''

import logging
import threading
import time

from dataprovider import DataProvider
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

import dataparser  # @UnresolvedImport

class NetworkDataProvider(DataProvider):
    """The DataService class provides a base class for any remote service such as
    oData or soap."""
    def __init__(self, url = None):
        self.timeout = 15
        self.pendingRequests = 0
        self.url = url
        self.request_list = []

    def setBasicAuth(self, username, password):
        """Once set, every request sent to the server will append a base-64
        encoded basicAuth header encoded with the provided username and password."""
        self.auth_header = {
            'Authorization': 'Basic ' + ('%s:%s' % (
            str(username), str(password))).encode('base-64'),
            'Accept': '*/*'}

    def _sendRequest(self, path, method, data = None, on_success = None, on_failure = None):
        """The 'Pedal to the metal'.  Send a UrlRequest with the appropriate callbacks."""
        def on_success_local(request, result):
            logging.info("Request successful".format())
            self.pendingRequests -= 1
            if on_success != None:
                on_success(request, result)

        def on_failure_local(request, result):
            status = request.resp_status
            if (status != None):
                logging.warning("Request failed with status ".format(request.resp_status))
            else:
                logging.warning("Request failed with no response")

            self.pendingRequests -= 1
            if on_failure != None:
                on_failure(request, result)

        logging.info("OData Request: {} {}".format(method, self.url + path))

        #TODO: Check to see if the url has a trailing '/'.
        request = UrlRequest(
            url = self.url + path,
            method = method,
            req_headers=self.auth_header,
            on_success=on_success_local,
            on_failure=on_failure_local,
            on_error=on_failure_local,
            timeout = self.timeout)

        self.request_list.append(request)

        self.pendingRequests += 1

class SoapProvider(NetworkDataProvider):
    pass

class ODataProvider(NetworkDataProvider):
    """
    ODataProvider interfaces with a remote oData service.  Data from requests
    are returned as an Entity or a set of Entities.
    """

    #TODO: This is a misnomer. It's more of a test of authentication credentials.
    def connect(self, url, username, password, on_success = None, on_failure = None):
        """
        Provides the kivy service with the target URL as well as credentials for
        basic authentication.  This also verifies that the username and password are
        valid credentials by attempting to pull the metadata from the target SAP
        gateway service.
        """
        self.setBasicAuth(username, password)
        self.url = url

        self.query(
            path = '$metadata',
            method = 'GET',
            on_success = on_success,
            on_failure = on_failure)

    def query(self, path, method = 'GET', on_success = None, on_failure = None):
        """Defines basic behavior on getEntity or getEntitySet."""

        #If we need need to parse our result...
        we_should_return_entities = method in ['GET']

        #Parse entities out of the result.  Call the callback with these results as params.
        #This should be called even if no callback is provided and the request is blocking.
        def on_success_local(request, result):
            if on_success != None:
                if we_should_return_entities:
                    #TODO: What are we doing with the parser?
                    #on_success(parser(result))
                    on_success(result)
                else:
                    on_success(result)

        #The default behavior if a request fails.
        def on_fail_local(request, result):
            #TODO: May not always have a response.  It may fail from no connection.

            if on_failure != None:
                on_failure(request.resp_status)

        self._sendRequest(
            path = path,
            method = method,
            on_success = on_success_local,
            on_failure = on_fail_local)

class ODataParser(object):
    """ HTTP Response goes in, Entity goes out """
    @classmethod
    def parseEntity(cls):
        pass
    
    @classmethod
    def parseEntities(cls):
        pass

class KivyClockSimulator(threading.Thread):
    """Since Kivy is built to be asynchronous, we need to have kivy's
    internal clock ticking."""
    _run_clock = False

    def run(self, *args):
        while (self._run_clock):
                Clock.tick()
                time.sleep(0.5)

    def startMainLoopSimulation(self):
        """Spawn a clock-ticking thread.  Make sure to call
        stopKivyMainLoopSimulation() when you are done with it.

        This is probably a horrible idea"""
        self._run_clock = True
        self.start()

    def stopMainLoopSimulation(self):

        self._run_clock = False

#if __name__ == "__main__":

    """
    import time

    GATEWAY_URL = "x"
    SERVICE_NAME = "x"
    
    USERNAME = 'x'
    PASSWORD = 'x'
    
    SERVICE_URL = GATEWAY_URL + SERVICE_NAME + '/'

    def onSuccess(**kwargs):
        print "hi"
        print kwargs

    def onFailure(**kwargs):
        print "bi"
        print kwargs

    KivyClockSimulator().startMainLoopSimulation()

    myService = ODataProvider()
    myService.connect(SERVICE_URL, USERNAME, PASSWORD)

    while myService.pendingRequests > 0:
        logging.info("Waiting on {} requests".format(myService.pendingRequests))

        for request in myService.request_list:
            logging.info("Request:\n\tURL: {}\n\tComplete:{}".format(request.url, request.is_finished))

        time.sleep(1)

    #myService.query('ProductSET', on_success = onSuccess, on_failure = onFailure)

    KivyClockSimulator().stopMainLoopSimulation()
    """

    """
    myObject = Entity()

    myObject['x'] = 3

    for keys, values in myObject.iteritems():
        print "{}:\t{}".format(keys, values)
    """
