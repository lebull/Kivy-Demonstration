#from bs4 import BeautifulSoup
#TODO: Proper docs? http://stackoverflow.com/questions/7500615/autogenerate-dummy-documentation-in-the-source-code-for-python-in-eclipse

import logging
from kivy.network.urlrequest import UrlRequest

class DataProvider(object):

    """True if the dataprovider can create, update, and delete new entities."""
    can_write = False   
    
    #CRUD
    #TODO: createEntity might be a little redundant.  Not sure what I think about it.
    def createEntity(self, **kwargs):
        if can_write:
            raise NotImplementedError()
        else:
            #TODO: Proper error
            raise Error('<classname> cannot write to its provider.')

    def getEntity(self, **kwargs):
        raise NotImplementedError()

    def getEntities(self, **kwargs):
        raise NotImplementedError()

    def _saveEntity(self, **kwargs):
        if can_write:
            raise NotImplementedError()
        else:
            raise Error('<classname> cannot write to its provider.')

    def _deleteEntity(self, **kwargs):
        if can_write:
            raise NotImplementedError()
        else:
            raise Error('<classname> cannot write to its provider.')
            
class NetworkDataProvider(DataProvider):
    """The DataService class provides a base class for any remote service such as
    oData or soap."""
    def __init__(self, url = None):
        self.timeout = 15
        self.pending_requests = 0
        self.request_list = []
        self.auth_header = {}

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
            if on_success != None:
                on_success(request, result)
            self.pending_requests -= 1

        def on_failure_local(request, result):
            status = request.resp_status
            if (status != None):
                logging.warning("Request failed with status {}".format(request.resp_status))
            else:
                logging.warning("Request failed with no response")

            if on_failure != None:
                on_failure(request, result)
            self.pending_requests -= 1
                
        # merging n dicts with dict comprehension 
        #http://hoardedhomelyhints.dietbuddha.com/2013/04/python-expression-idiom-merging.html
        req_headers = {k:v for d in (req_headers, self.auth_header) for k, v in d.iteritems()}

        logging.info("Request: {} {}".format(method, url))

        request = UrlRequest(
                             url        = url,
                             method     = method,
                             req_headers= req_headers, #Combining dictionaries
                             req_body   = req_body,
                             on_success = on_success_local,
                             on_failure = on_failure_local,
                             on_error   = on_failure_local,
                             timeout    = self.timeout,
                             debug      = False)


        self.request_list.append(request)
        self.pending_requests += 1

if __name__ == "__main__":
    pass
    #from kivy.clock import Clock
    #If testing networkdataprovider, be sure to use the clock :D

#TODO: SQLite provider


