import logging

#import re
from bs4 import BeautifulSoup

from dataprovider import NetworkDataProvider
from entity import Entity

from bs4.element import NavigableString

class SoapProvider(NetworkDataProvider):
    
    can_write = False
    
    def __init__(self, url, **kwargs):
        """
        :string url:
        :kwargs:
        """
        self.url    = url
        self.actions = {}
        super(SoapProvider, self).__init__(**kwargs)
        self._populateActions()
        
    def _populateActions(self):
        """Retrieves the actions that are associated with this service.
        Called in the constructor."""     
        def on_success_local(request, result):
            logging.info("WSDL acquired.")
            self.actions = SoapResponseParser.getActionsFromWsdl(result)
                
        def on_fail_local(request, result):
            logging.warning(
                "Request to get WSDL failed:" + 
                "\n\tURL:{url}\n\tResponse:{status}".format(url = request.url, 
                                                     status = request.resp_status))
        
        self._sendRequest(url   = self.url + "?WSDL", 
                  method        = 'GET', 
                  on_success    = on_success_local, 
                  on_failure    = on_fail_local)

    def query(self, action, keys, on_success = None, on_failure = None):
        """
        Call an action for the soap service.
        :string action:
        :any[] keys:
        :function on_success:
        :function on_failure:
        ..todo: Allow the user to give the desired root via name.
        """

        #TODO: Dumb, don't block while we wait on actions.
        if self.actions == {}:
            self.wait()
            
        assert action in self.actions.keys()
        
        def on_fail_local(request, result):
            print "FAIL :("
            print request.result
        
        def on_success_local(request, result):
            print "SUCCESS!!"
            returnEntity = SoapResponseParser.getEntityFromQuery(result)
            
            if on_success != None:
                on_success(returnEntity)
            
        #Build our SOAP request.
        soap_request = SoapRequestBuilder( url         = self.url, 
                                    action_url  = self.actions[action],
                                    keys        = keys)
        
        self._sendRequest(url           = soap_request.url, 
                          method        = soap_request.method, 
                          req_headers   = soap_request.headers, 
                          req_body      = soap_request.body, 
                          on_success    = on_success_local, 
                          on_failure    = on_fail_local)
        
    def getActions(self):
        """
        Return a list of actions.
        @todo block while we are waiting on actions from the wsdl.
        """
        return self.actions.keys()
        
class SoapRequestBuilder(object):
    """A soapRequestBuilder object represents a single soap request."""
    
    body_template = {
        '1.1': 
"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{action} xmlns="http://tempuri.org/">
      {keys}
    </{action}>
  </soap:Body>
</soap:Envelope>""",

        '1.2': 
"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <{action} xmlns="{action_url}">
      {keys}
    </{action}>
  </soap12:Body>
</soap12:Envelope>"""
    }
    
    def __init__(self, url, action_url, keys, version = '1.2'):
        """
        :string url:    Points to the Soap Service
        :string action_url: Points to the Soap Action.  Use *only* the full URL.
        :string version: can be '1.1' or '1.2'
        """
        #assert url in self.body_template.keys()
   
        self.url = url
        self.action_url = action_url
        
        self.action_url, self.action = self.action_url.rsplit('/', 1)
        self.action_url = self.action_url + "/"
        
        self.method = 'POST'
        self.headers = {'Content-Type' : 'application/soap+xml; charset=utf-8'}
        
        #Add the soapaction header in 
        if(version == '1.1'):
            self.headers['SOAPAction'] = self.action
        
        keys_string = ""
        for key, value in keys.iteritems():
            keys_string += "<{key}>{value}</{key}>".format(key    = key, 
                                                           value  = value)
        
        self.body = self.body_template[version].format(url          = self.url,
                                                       action       = self.action,
                                                       action_url   = self.action_url, 
                                                       keys         = keys_string)
        
    def __str__(self):
        
        returnString = ""
        
        returnString += "Url:\t{}".format(self.url)

        headerString = ""
        for key, value in self.headers.iteritems():
            headerString += "\n{}: {}".format(key, value)
        
        returnString += "\n" + headerString
        returnString += "\n\n" + self.body
    
        return returnString
    
class SoapResponseParser(object):
    """Static class to parse incoming soap responses."""
    #TODO: Regexes to avoid namespace conflicts.  This should be fun...
    
    @classmethod
    def getActionsFromWsdl(cls, wsdl_data):
        """Parses out soapaction's from WSDL files.  This will be used to get an
        action's url from the action itself.
        
        :string wsdl_data:
        """
        actions = {}
        
        operations = BeautifulSoup(wsdl_data).findAll('soap:operation')
        for operation in operations:
            action_location = operation.attrs['soapaction']
            action_name = operation.parent.attrs['name']
            actions[action_name] = action_location
            
        return actions
    
    @classmethod
    def getEntityFromQuery(cls, result):
        """Converts a soap response into an entity or entities.  
        It will return a tree of entities, but the leaf nodes (hopefully
        a collection of attributes) will be represented as dictionaries.  
        Otherwise, you would have an entity for every individual attribute.
        
        @param result:
        @type string:
        """
        
        soup = BeautifulSoup(result)
        response = soup.find('soap:body')
        return cls._getEntityFromSoup(response)

        
        
    @classmethod
    def _getEntityFromSoup(cls, soup):
        """Recursively scans soup and assembles an entity tree.  If yadida"""
        
        return_value = None
        return_entity = Entity()
        
        is_leaf = True #Set to false if it is discovered that this is not a leaf element.
        
        for child in soup.contents:
            name = child.name
            #if child node
            if type(child) == NavigableString:
                
                #TODO: try to get the type of this from the wsdl.
                return_value = child
            
            #not child node
            else:
                is_leaf = False             
                return_entity[name] = cls._getEntityFromSoup(child)
        
        #If this is the leaf, then we return a dict.
        if is_leaf:
            return return_value
        #If not, return an Entity.
        else:
            return return_entity
        
if __name__ == "__main__":
    from kivyClockSimulator import ClockSim


    
    def print_entity(entity):
        print entity.prettyString()
    
    def testWeather():
        dp = SoapProvider("http://wsf.cdyne.com/WeatherWS/Weather.asmx")
        
        dp.query(action = "GetCityWeatherByZIP",
                 keys   = {"ZIP": "38654"},
                 on_success = print_entity)
        
        dp.wait()
    
    def main():
        clocksim = ClockSim()
        clocksim.start()
        testWeather()
        clocksim.stop()
        
    main()
    
