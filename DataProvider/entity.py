"""
Entities hold data.  Data is good.
"""

#import json

class Entity(dict):
    '''An Entity is an object created to hold general data allow data to be 
    created, updated, or deleted from its corrisponding database.
    
    The Entity class inherits from python's native dictionary and the Entity's
    properties are stored in that dictionary.

        >>> apple = Entity()
        >>> apple['color'] = red
        
    For convenience, you can also access an Entity's properties through attribute
    access.
    
        >>> print apple.color
    
    Entities are spawned by DataProviders.
    
        >>> DataProvider().asdfasdf
    
    An entity can be created without a DataProvider, but it's useful if it is
    associated with an existing DataProvider.  This way, you can update or delete
    the entity without any direct calls to its data provider.
    '''
    
#     Example of overloading __getatr__ and __setattr__
#     This example creates a dictionary where members can be accessed as attributes
#     http://code.activestate.com/recipes/389916-example-setattr-getattr-overloading/
    def __init__(self, properties=None, key = None, data_provider = None):
        '''
        :Parameters:
            `properties`: dict 
            `key`: string
            `data_provider`: DataProvider
        '''

        assert type(properties) == dict or properties == None

        #: Parent DataProvider
        self.data_provider = data_provider
        #: The key.  Not required.  Not sure if useful.
        self.key = key
        self._loading_url = ""
        self._loaded = properties != None #If we are giving it some initial properties, we're calling it loaded.

        #Initial Attributes
        if properties is None:
            properties = {}
        # set any attributes here - before initialization
        # these remain as normal attributes

        dict.__init__(self, properties)
        self.__initialised = True
        # after initialization, setting attributes is the same as setting an item

    def __getattr__(self, item):
        '''Maps values to attributes. 
        Only called if there *isn't* an attribute with this name
        '''
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        '''Maps attributes to values. Only if we are initialized
        '''
        if not self.__dict__.has_key('_attrExample__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, item, value)
        elif self.__dict__.has_key(item):       # any normal attributes are handled normally
            dict.__setattr__(self, item, value)
        else:
            self.__setitem__(item, value)
            
    def __str__(self):
        if self.key != None:
            return "Entity"
        else:
            return "Entity({})".format(self.key)

#     def jsonEncode(self):
#         """Returns a json representation of an entity."""
#  
#         return json.dumps(self.__dict__)
#  
#     @classmethod
#     def jsonDecode(cls, json_data):
#         """Takes a json representation of an entity and returns it as an Entity object."""
#         data = json.loads(json_data)
#         return Entity(properties = data)
        
    def save(self):
        '''Save the entity in its assigned database.
        '''
        if(self.data_provider != None):
            try:
                self.data_provider._saveEntity(self)
            except:
                #TODO: Right error
                print "Problem Saving Entity"

        else:
            #TODO: Throw error that entity has no parent data provider
            print "No Data Provider"

    def delete(self):
        '''Delete the entity from its assigned database.
        '''
        if(self.data_provider == None):
            try:
                self.data_provider._deleteEntity(self)
            except:
                #TODO: Right error
                print "Problem Deleting Entity"
        else:
            #TODO: Throw error that entity has no parent data provider
            print "No Data Provider"
            

#     def loadEntity(self):
#         assert self.data_provider != None
#         assert self._loading_url != None
#          
#         def load_properties(entities):
#             new_entity = entities[0]
#             self.properties = new_entity.properties
#              
#         self.data_provider.query(self._loading_url, on_success = load_properties)
#         self.data_provider.wait()

        
    def prettyString(self, indent = 0):
        '''
        :Parameters:
            `indent` : int
                The indent level for the string.
        '''
        
        returnString = ""
        returnString += "Entity({})\n".format(self.key)
        
        #Wow, this is a fun line...
        
        for key, value in self.iteritems():
            
            if isinstance(value, Entity):
                value = value.prettyString(indent + 1)
             
            returnString += "\t" * (indent + 1) + "{}: {}\n".format(key, value)
            
        return returnString
            
#TODO: JSON Encoder and Decoder.