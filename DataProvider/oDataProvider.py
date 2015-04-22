from dataprovider import NetworkDataProvider, CrudDataProvider
from entity import Entity
import json
from docutils.parsers.rst.directives import path

#TODO: lets point to a single on_fail function.

class ODataProvider(NetworkDataProvider, CrudDataProvider):
    """
    ODataProvider interfaces with a remote oData service.  Data from requests
    are returned as an Entity or a set of Entities.
    
    ODataProvider requests for the oData to be returned as JSON and will *only*
    be compatible with those that can return oData as json.
    """
    
    def __init__(self, **kwargs):
        super(ODataProvider, self).__init__(**kwargs)
        
        self.datatypes = {}
        self.latestversion = ""

    #TODO: This is a misnomer. It's more of a test of authentication credentials.
    def connect(self, username, password, 
                on_success = None, on_failure = None):
        """
        Provides the kivy service with the target URL as well as credentials for
        basic authentication.  This also verifies that the username and password are
        valid credentials by attempting to pull the metadata from the target SAP
        gateway service.
        """
        
        def on_success_local(request, result):
            self.datatypes = result
            #Drill down while there is only one node in our dict.
            while len(self.datatypes) == 1:
                self.datatypes = self.datatypes.items()[0][1]
            if on_success != None:
                on_success(result)
        
        self.setBasicAuth(username, password)
                
        self._sendRequest(
            url = self.url + '?$format=json', #TODO: Support other parameters.
            method = 'GET',
            on_success = on_success_local,
            on_failure = on_failure)

    def getEntity(self, path, 
                  on_success = None, on_failure = None, wait = False):
        """Returns a single entities"""

        def on_success_local(request, result):
            if on_success != None:
                on_success(ODataParser.parseEntityFromDict(result, odata_provider = self))
                
        self._getSomething(path         = path,
                           on_success   = on_success_local,
                           on_failure   = on_failure,
                           wait         = wait)

    def getEntities(self, path, 
                    on_success = None, on_failure = None, wait = False):
        """Returns a collection of entities"""
        
        def on_success_local(request, result):
            if on_success != None:
                on_success(ODataParser.parseEntitiesFromDict(result, odata_provider = self))
                
        self._getSomething(path         = path,
                           on_success   = on_success_local,
                           on_failure   = on_failure,
                           wait         = wait)
        
    def _getSomething(self, path, 
                      on_success = None, on_failure = None, wait = False):
        
        path = self._validatePath(path)
        
        self._sendRequest(
            url         = self.url + path + '?$format=json' ,         #TODO: Support other parameters.
            method      = 'GET',
            on_success  = on_success,
            on_failure  = on_failure,
            wait        = wait)
        
    def _validatePath(self, path):
        #TODO: Check if path contains a url that's not the current url.
        #Get rid of the url if it is in there.
        path = path.replace(self.url, "")
        return path

#private
class ODataParser(object):
    """Parses a python dictionary into an ODataEntity"""
    @classmethod
    def parseEntityFromDict(cls, data_dict, odata_provider):

        #The first layer is just a wrapper, so knock it off.
        data_dict = data_dict.popitem()[1]
        data_dict = cls._convertDeferredToUnloadedEntities(data_dict, odata_provider)
        return ODataEntity(properties=data_dict)
        
    @classmethod
    def parseEntitiesFromDict(cls, data_dict, odata_provider):
        """This method returns either a single entity or an array of entities.  This
        is determined by the format of the oData that is returned.  Just kidding, the
        two variables actually fight to the death."""
        
        #The first layer is just a wrapper, so knock it off.
        clensed_data_dict = data_dict.popitem()[1]
        
        clensed_data_dict = clensed_data_dict['results']
        
        #Loop through every entry and create an entity out of it.
        returnEntities = []
        for entity_properties in clensed_data_dict:
            #Replace _deferred with UnloadedQuery
            entity_properties = cls._convertDeferredToUnloadedEntities(entity_properties, odata_provider)
            returnEntities.append(ODataEntity(properties=entity_properties, data_provider = odata_provider))
        return returnEntities
    
    @classmethod
    def _convertDeferredToUnloadedEntities(cls, properties, odata_provider):
        
        for key, value in properties.iteritems():
            if type(value) == dict:
                if key == "__deferred":
                    #TAG: Can this contain multiple uris?.
                    properties = UnloadedQuery(uri = value['uri'], odata_provider = odata_provider)
                else:
                    #We need to convert the sub-dictionary
                    properties[key] = cls._convertDeferredToUnloadedEntities(value, odata_provider)
                
        return properties
    
              
class ODataEntity(Entity):
    
    #TODO: Load metadata into its own instance attribute :3
    def __getattr__(self, item):
        #If we try to access an UnloadedQuery, then we need to load that
        #entity set
        returnItem = super(ODataEntity, self).__getattr__(item)
        if type(returnItem) == UnloadedQuery:
            returnItem = returnItem.getEntities()
        return returnItem

#Private
class UnloadedQuery(object):
    '''
    .. todo::
        Convert to UnloadedEntity
    '''
    def __init__(self, uri, odata_provider):
        self.uri = uri
        self.odata_provider = odata_provider

    def getEntities(self):
        #TODO: There has to be another way to get around this namespace crap.
        #Ohmygod python is not good with namespaces in the asynchronous world.  Make it stahp!
        
        return_entities = [[]]
        error = [False] #TAG: Wrapped in an array because of the namespace issues.  Sorry :x
        
        def on_success_local(entities):
            return_entities[0] = entities
        
        def on_failure_local(request, result):
            error[0] = [True]
        
        self.odata_provider.getEntities(path = self.uri,
                                        on_success = on_success_local,
                                        on_failure = on_failure_local,
                                        wait = True)
        
        if error[0] == True:
            raise RuntimeError('Issue with loading an UnloadedQuery')
            #TODO: Raise an...attribute error?
        else:
            return return_entities[0]
        #TODO: Catch a ResultMismatch exception, then try with getEntity.
        
    def __str__(self):
        return "(UnloadedQuery - {})".format(self.uri)


#TODO: Errors for: 
#
#ResultMismatch
#    Try to get multiple entities when result is formatted for one.
#    Visa Versa

#UnloadedQuery cannot load entities from uri.
