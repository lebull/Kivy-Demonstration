from dataprovider import NetworkDataProvider, CrudDataProvider
from entity import Entity
import json

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
    def connect(self, username, password, on_success = None, on_failure = None):
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


    def query(self, path, method = 'GET', on_success = None, on_failure = None):
        """Defines basic behavior on getEntity or getEntitySet."""
        
        #Get rid of the url if it is in there.
        
        path = path.replace(self.url, "")

        #If we need need to parse our result...
        we_should_return_entities = method in ['GET']

        #Parse entities out of the result.  Call the callback passing the resulting entities.
        def on_success_local(request, result):
            if on_success != None:
                if we_should_return_entities:
                    #TODO: Parse out entities
                    entities = ODataParser.parseEntitiesFromDict(result)
                    on_success(entities)
                else:
                    on_success(result)

        #The default behavior if a request fails.
        def on_fail_local(request, result):
            #TODO: May not always have a response.  It may fail from no connection.

            if on_failure != None:
                on_failure(request, result)
        
        self._sendRequest(
            url = self.url + path + '?$format=json' ,         #TODO: Support other parameters.
            method = method,
            on_success = on_success_local,
            on_failure = on_fail_local)
        


class ODataParser(object):
    
    @staticmethod
    def parseEntitiesFromDict(data_dict):
        """This method returns either a single entity or an array of entities.  This
        is determined by the format of the oData that is returned.  Just kidding, the
        two variables actually fight to the death."""
        
        #So does this method return one entity or multiple?  Only time will tell!
        winner = 'returnEntities' #Looks like we have a crowd favorite!
        returnEntity = None
        returnEntities = []
        
        #FIGHT TO THE DEATH
        
        #The first layer of 
        data_dict = data_dict.popitem()[1]
        
        #If the next layer is results, we return an array.  If not, we return a
        #single entity
        try:
            data_dict = data_dict['results'] #Looks like returnEntities is starting off strong.  Right in the gonads!
            
            #Loop through every entry and create an entity out of it.
            for data_row in data_dict:
                returnEntities.append(Entity(properties=data_row))
            
        except AttributeError:
            winner = 'returnEntity'     #UNBELIEVABLE!  he just came out of nowhere and took victory from the jaws of defeat!
            returnEntity = Entity(properties=data_dict) 
            
        finally: #Here we are in the winner's circle
            if winner == 'returnEntities':
                return returnEntities    #GG
            elif winner == 'returnEntity':
                return returnEntity      #GG
            else:
                return "Everyone's money.  Not a good fight :(" #BG
        
        #TODO: Convert _deferred to unloaded entities

    
    
    
    

    #http://sapgwvci.ipaper.com:8025/sap/opu/odata/sap/YNI_SPIDER_SRV/?$format=xml
    #http://sapgwvci.ipaper.com:8025/sap/opu/odata/sap/YNI_SPIDER_SRV/$metadata?$format=json