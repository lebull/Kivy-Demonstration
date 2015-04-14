#from bs4 import BeautifulSoup
#TODO: Proper docs? http://stackoverflow.com/questions/7500615/autogenerate-dummy-documentation-in-the-source-code-for-python-in-eclipse

import logging

import time

from kivy.network.urlrequest import UrlRequest


class CrudDataProvider(object):

    #CRUD
    #TODO: createEntity might be a little redundant.  Not sure what I think about it.
    def createEntity(self, **kwargs):
        raise NotImplementedError()

    def getEntity(self, **kwargs):
        raise NotImplementedError()

    def getEntities(self, **kwargs):
        raise NotImplementedError()

    def _saveEntity(self, **kwargs):
        raise NotImplementedError()

    def _deleteEntity(self, **kwargs):
        raise NotImplementedError()
            
class NetworkDataProvider(object):
    """The DataService class provides a base class for any remote service such as
    oData or soap."""
    
    def __init__(self, url = None):
        """
        :param url:
        :type url: string
        """
        self.timeout = 15
        self.pending_requests = 0
        self.request_list = []
        self.auth_header = {}
        
        self.url = url
        

    def setBasicAuth(self, username, password):
        """Once set, every request sent to the server will append a base-64
        encoded basicAuth header encoded with the provided username and password."""
        
        self.auth_header = {
            'Authorization': 'Basic ' + ('%s:%s' % (
            str(username), str(password))).encode('base-64'),
            'Accept': '*/*'}

    def _sendRequest(self, url, method, req_headers = {}, req_body = None, on_success = None, on_failure = None):
        """Send a UrlRequest with the appropriate callbacks.
        
        @todo implement on_update
        :param path:
        :param path:
        :param method:
        :param req_headers:
        :param req_body:
        :param on_success:
        :param on_failure:
        
        :type path: string ladeda
        :type path: string
        :type method: string
        :type req_headers: dict
        :type req_body: string
        :type on_success: function
        :type on_failure: function
        """
        
        def on_success_local(request, result):
            on_always_local(request, result)
            if on_success != None:
                on_success(request, result)

        def on_failure_local(request, result):
            on_always_local(request, result)
            if on_failure != None:
                on_failure(request, result)
            
        def on_always_local(request, result):
            #Print the return status to the log
            status = request.resp_status
            
            if (status != None):
                if status == 200:
                    logging.info("Request completed successfully")
                else:
                    logging.warning("Request failed with status {}".format(status))
            else:
                logging.warning("Request failed with no response")

            #Subtract the number of pending requests.
            self.pending_requests -= 1
                
        # merging n dicts with dict comprehension 
        #http://hoardedhomelyhints.dietbuddha.com/2013/04/python-expression-idiom-merging.html
        req_headers = {k:v for d in (req_headers, self.auth_header) for k, v in d.iteritems()}

        logging.info("Request: {} {}".format(method, url))

        #Remember that if UrlRequest gets back json, it automatically converts
        #the result to json.  I think it's kinda silly, but oh well.  If you
        #ever want to fork this project to use another library, make sure to take
        #this into account.
        request = UrlRequest(url        = url,
                             method     = method,
                             req_headers= req_headers, #Combining dictionaries
                             req_body   = req_body,
                             on_success = on_success_local,
                             on_failure = on_failure_local,
                             on_error   = on_failure_local,
                             timeout    = self.timeout)

        self.request_list.append(request)
        
        self.pending_requests += 1
        
    def wait(self):
        """Block until the dataprovider has no pending requests"""
        while self.pending_requests > 0:
            time.sleep(0.5)
            
    #TODO:  have an "ordered wait" that waits until all current request are
    #complete but ignores any requests made afterwards.

if __name__ == "__main__":
    pass
    #from kivy.clock import Clock
    #If testing networkdataprovider, be sure to use the clock :D

#TODO: SQLite provider


