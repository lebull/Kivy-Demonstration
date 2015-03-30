import logging

from dataprovider import NetworkDataProvider

from bs4 import BeautifulSoup

class SoapProvider(NetworkDataProvider):
    
    can_write = False
    
    def __init__(self, url, **kwargs):
        self.url    = url
        self.actions = {}
        
        super(SoapProvider, self).__init__(**kwargs)
        
        self.getActions()
        
    def getActions(self):
        
        #TODO:  Block somehow until we have our actions.
        
        def on_success_local(request, result):
            actions = BeautifulSoup(result).findAll('soap:operation')
            for action in actions:
                action_location = action.attrs['soapaction']
                action_name = action.parent.attrs['name']
                self.actions[action_name] = action_location
                

        def on_fail_local(request, result):
            logging.warning(
                "Request to get WSDL failed:\n\tURL:{url}\n\tResponse:{status}".format(url = request.url, 
                                                                                       status = request.resp_status))
        
        self._sendRequest(url   = self.url + "?WSDL", 
                  method        = 'GET', 
                  on_success    = on_success_local, 
                  on_failure    = on_fail_local)

    def query(self, url, action, keys, on_success = None, on_failure = None):
        """
        In url, be sure to include ?WSDL
        """
        
        def on_fail_local(request, result):
            print "FAIL :("
            print request.result
        
        def on_success_local(request, result):
            print "SUCCESS!!"
            print request.resp_status
            #TODO: parse and return the response.
            
        #Build our SOAP request.
        mySoapRequest = SoapRequest(url     = url, 
                                    action  = action, 
                                    keys    = keys)
        
        self._sendRequest(url           = mySoapRequest.url, 
                          method        = mySoapRequest.method, 
                          req_headers   = mySoapRequest.headers, 
                          req_body      = mySoapRequest.body, 
                          on_success    = on_success_local, 
                          on_failure    = on_fail_local)
        
        

class SoapRequest(object):
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
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">  <soap12:Body>
  <soap12:Body>
    <{action} xmlns="{url}">
      {keys}
    </{action}>
  </soap12:Body>
</soap12:Envelope>"""
    }
    
    def __init__(self, url, action, keys, version = '1.2'):
        """
        @param version can be '1.1' or '1.2'
        @type string
        """
        #assert url in self.body_template.keys()

   
        self.url = url
        self.action = action

        self.method = 'POST'
        self.headers = {
            'Content-Type'  :   'application/soap+xml; charset=utf-8',
            #'SOAPAction'    :   'GetCityWeatherByZIP',
            #'SOAPAction'.encode(encoding):       "http://tempuri.org/{action}".format(action = action).encode(encoding)
        }
        
        keys_string = ""
        for key, value in keys.iteritems():
            keys_string += "<{key}>{value}</{key}>".format(key    = key, 
                                                           value  = value)
        
        self.body = self.body_template[version].format(url      = self.url,
                                                       action   = self.action, 
                                                       keys     = keys_string)
        
    def __str__(self):
        
        returnString = ""
        
        returnString += "Url:\t{}".format(self.url)

        headerString = ""
        for key, value in self.headers.iteritems():
            headerString += "\n{}: {}".format(key, value)
        
        returnString += "\n" + headerString
        returnString += "\n\n" + self.body
    
        return returnString
        
if __name__ == "__main__":
    import kivyClockSimulator
    import time
    
    #http://wsf.cdyne.com/WeatherWS/Weather.asmx?op=GetCityWeatherByZIP

    dp = SoapProvider("http://wsf.cdyne.com/WeatherWS/Weather.asmx")
    
    
    #dp.query(action = "GetCityWeatherByZIP",
    #         keys   = {"ZIP": "38654"})

    
    clocksim = kivyClockSimulator.KivyClockSimulator(network_providers = [dp])
    clocksim.startMainLoopSimulation()
    
    while clocksim.is_alive():
        time.sleep(0.5)
        
    print dp.actions
        
    print dp.request_list[0].is_finished
    
