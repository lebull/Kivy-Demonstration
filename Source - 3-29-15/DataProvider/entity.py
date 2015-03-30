"""
Entity holds data.  Data good.
"""

#import json

class Entity(dict):
    
#     Example of overloading __getatr__ and __setattr__
#     This example creates a dictionary where members can be accessed as attributes
#     http://code.activestate.com/recipes/389916-example-setattr-getattr-overloading/
    def __init__(self, properties=None, key = None, data_provider = None):

        #Parent DataProvider
        self.data_provider = data_provider
        self.key = key

        #Initial Attributes
        if properties is None:
            properties = {}
        # set any attributes here - before initialization
        # these remain as normal attributes

        dict.__init__(self, properties)
        self.__initialised = True
        # after initialization, setting attributes is the same as setting an item

    def __getattr__(self, item):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        """Maps attributes to values. Only if we are initialized"""
        if not self.__dict__.has_key('_attrExample__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, item, value)
        elif self.__dict__.has_key(item):       # any normal attributes are handled normally
            dict.__setattr__(self, item, value)
        else:
            self.__setitem__(item, value)
            
    def __str__(self):
        returnString = ""
        returnString += "Entity - key: {}\n".format(self.key)
        
        #Wow, this is a fun line...
        returnString += "\n".join(["\t{}: {}".format(key, value) for key, value in self.iteritems()])
        return returnString

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
        """Save the entity in its assigned database."""
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
        """Delete the entity from its assigned database."""
        if(self.data_provider == None):
            try:
                self.data_provider._deleteEntity(self)
            except:
                #TODO: Right error
                print "Problem Deleting Entity"
        else:
            #TODO: Throw error that entity has no parent data provider
            print "No Data Provider"
            
#TODO: JSON Encoder and Decoder.