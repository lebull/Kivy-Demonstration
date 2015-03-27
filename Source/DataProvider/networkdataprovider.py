"""It's dataprovider, but networked"""

import logging
import threading
import time

from dataprovider import DataProvider
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

from bs4 import BeautifulSoup
import urlparse
from __builtin__ import True

#import dataparser  # @UnresolvedImport

class NetworkDataProvider(DataProvider):
    """The DataService class provides a base class for any remote service such as
    oData or soap."""
    def __init__(self, url = None):
        self.timeout = 15
        self.pending_requests = 0
        self.url = url
        self.request_list = []
        self.auth_header = {}

    def setBasicAuth(self, username, password):
        """Once set, every request sent to the server will append a base-64
        encoded basicAuth header encoded with the provided username and password."""
        self.auth_header = {
            'Authorization': 'Basic ' + ('%s:%s' % (
            str(username), str(password))).encode('base-64'),
            'Accept': '*/*'}

    def _sendRequest(self, path, method, req_headers = None, req_body = None, on_success = None, on_failure = None):
        """The 'Pedal to the metal'.  Send a UrlRequest with the appropriate callbacks.
        
        @param path
        @type string
        
        @param method
        @type string
        
        @param req_headers
        @type dict
        
        @param req_body
        @type string
        
        @param on_success
        @type function
        
        @param on_failure
        @type function
        
        """
        def on_success_local(request, result):
            logging.info("Request successful".format())
            self.pending_requests -= 1
            if on_success != None:
                on_success(request, result)

        def on_failure_local(request, result):
            status = request.resp_status
            if (status != None):
                logging.warning("Request failed with status ".format(request.resp_status))
            else:
                logging.warning("Request failed with no response")

            self.pending_requests -= 1
            if on_failure != None:
                on_failure(request, result)
                
        # merging n dicts with dict comprehension 
        #http://hoardedhomelyhints.dietbuddha.com/2013/04/python-expression-idiom-merging.html
        req_headers = {k:v for d in (req_headers, self.auth_header) for k, v in d.iteritems()}

        logging.info("Request: {} {}".format(method, self.url + path))

        #TODO: Check to see if the url has a trailing '/'.
        request = UrlRequest(
            url = self.url + path,
            method = method,
            req_headers=req_headers, #Combining dictionaries
            req_body= req_body,
            on_success=on_success_local,
            on_failure=on_failure_local,
            on_error=on_failure_local,
            timeout = self.timeout)

        self.request_list.append(request)

        self.pending_requests += 1

class SoapProvider(NetworkDataProvider):
    can_write = False

    def getEntity(self, action, key, value, on_success = None, on_failure = None):

        def on_fail_local(request, result):
            print request.req_headers
        
        #TODO: on_success_local to parse out the response.
        def on_success_local(request, result):
            print request.url
                
        action = "GetSecureIPUser"
        
        key = "userPrincipalName"
        
        value = "tdarsey"
        
#         header = """POST /radssecurityws/wsmembership.asmx HTTP/1.1
#         Host: radssvcdev.ipaper.com
#         Content-Type: text/xml; charset=utf-8
#         Content-Length: length
#         SOAPAction: "http://tempuri.org/{action}"
#         """
        
        
        #TODO: Support for multiple values.
        req_body = """
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{action} xmlns="http://tempuri.org/">
      <{key}>{value}</{key}>
    </{action}>
  </soap:Body>
</soap:Envelope>
        """.format(action = action, key = key, value = value)
        
        req_body = req_body.encode('utf-8')

        req_headers = {
            'Host'.encode('utf-8'):             'radssvcdev.ipaper.com'.encode('utf-8'),
            'Content-Type'.encode('utf-8'):     'text/xml; charset=utf-8'.encode('utf-8'),
            'Content-Length'.encode('utf-8'):   str(len(req_body)).encode('utf-8'),
            'SOAPAction'.encode('utf-8'):       "http://tempuri.org/{action}".format(action = action).encode('utf-8')
        }


        print req_headers
        print req_body

        #TODO: Build soap body
        
        self._sendRequest(path          = "", 
                          method        = "POST", 
                          req_headers   = req_headers, 
                          req_body      = req_body, 
                          on_success    = on_success_local, 
                          on_failure    = on_fail_local)
        
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
        """Parse a single entity"""
        pass
    
    @classmethod
    def parseEntities(cls):
        """Parse many entities"""
        pass

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
        
        super(KivyClockSimulator, self).__init__(*kwargs)
        
    def run(self, *args):
        while (self._run_clock):
                
                if(self.stop_when_requests_done 
                   and self.checkRequestsRemain()):
                    self.stopMainLoopSimulation()
                    print "Stopping"
                Clock.tick()
                time.sleep(0.5)
                
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


if __name__ == "__main__":
    
    
    dp = SoapProvider(url = "___")
    
    clocksim = KivyClockSimulator(network_providers = [dp])
    clocksim.startMainLoopSimulation()
    
    dp.getEntity(action     = "GetSecureIPUser",
                 key        = "userPrincipalName", 
                 value      = "tdarsey")
#     """
#     import time
# 
#     GATEWAY_URL = "x"
#     SERVICE_NAME = "x"
#     
#     USERNAME = 'x'
#     PASSWORD = 'x'
#     
#     SERVICE_URL = GATEWAY_URL + SERVICE_NAME + '/'
# 
#     def onSuccess(**kwargs):
#         print "hi"
#         print kwargs
# 
#     def onFailure(**kwargs):
#         print "bi"
#         print kwargs
# 
#     KivyClockSimulator().startMainLoopSimulation()
# 
#     myService = ODataProvider()
#     myService.connect(SERVICE_URL, USERNAME, PASSWORD)
# 
#     while myService.pending_requests > 0:
#         logging.info("Waiting on {} requests".format(myService.pending_requests))
# 
#         for request in myService.request_list:
#             logging.info("Request:\n\tURL: {}\n\tComplete:{}".format(request.url, request.is_finished))
# 
#         time.sleep(1)
# 
#     #myService.query('ProductSET', on_success = onSuccess, on_failure = onFailure)
# 
#     KivyClockSimulator().stopMainLoopSimulation()
#     """
# 
#     """
#     myObject = Entity()
# 
#     myObject['x'] = 3
# 
#     for keys, values in myObject.iteritems():
#         print "{}:\t{}".format(keys, values)
#    """
