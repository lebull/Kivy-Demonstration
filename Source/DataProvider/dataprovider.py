#from bs4 import BeautifulSoup

import json

class Entity(dict):
    """Example of overloading __getatr__ and __setattr__
    This example creates a dictionary where members can be accessed as attributes
    http://code.activestate.com/recipes/389916-example-setattr-getattr-overloading/
    """
    def __init__(self, id = None, properties=None, data_provider = None):

        #Parent DataProvider
        self.data_provider = data_provider
        self.id = id

        #Initial Attributes
        if properties is None:
            properties = {}
        # set any attributes here - before initialisation
        # these remain as normal attributes

        dict.__init__(self, properties)
        self.__initialised = True
        # after initialisation, setting attributes is the same as setting an item

    def __getattr__(self, item):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        """Maps attributes to values.
        Only if we are initialised
        """
        if not self.__dict__.has_key('_attrExample__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, item, value)
        elif self.__dict__.has_key(item):       # any normal attributes are handled normally
            dict.__setattr__(self, item, value)
        else:
            self.__setitem__(item, value)

    def jsonEncode(self):
        """Returns a json representation of an entity."""

        return json.dumps(self.__dict__)

    @classmethod
    def jsonDecode(cls, json_data):
        """Takes a json representation of an entity and returns it as an Entity object."""
        data = json.loads(json_data)
        return Entity(properties = data)
        

    def create(self):
        """ Saves a copy of an entity's """
        if(self.data_provider == None):
            #TODO: Try/catch to save the entity through its data provider
            pass
        else:
            #TODO: Throw error that entity has no parent data provider
            pass

    def save(self):
        if(self.data_provider == None):
            #TODO: Try/catch to save the entity through its data provider
            pass
        else:
            #TODO: Throw error that entity has no parent data provider
            pass

    def delete(self):
        if(self.data_provider == None):
            #TODO: Try/catch to delete the entity through its data provider
            pass
        else:
            #TODO: Throw error that entity has no parent data provider
            pass

class DataProvider(object):

    """True if the dataprovider can create, update, and delete new entities."""
    can_write = False   

    def createEntity(self, entity):
        raise NotImplementedError()

    def getEntity(self, id):
        raise NotImplementedError()

    def getEntities(self):
        raise NotImplementedError()

    def saveEntity(self, entity):
        raise NotImplementedError()

    def deleteEntity(self, entity):
        raise NotImplementedError()

class JSONDataProvider(DataProvider):
    """A dataprovider which is kept locally as a json file."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {}
        self._loadData()

    def _loadData(self):
        try:
            myFile = open(self.filepath, 'r')
            self.data = json.load(myFile)
            myFile.close()
        except IOError:
            pass
            #TODO: Do we wana handle this at all?

    def _saveData(self):
        json_file = open(self.filepath, 'w+')
        json.dump(self.data, json_file)
        json_file.close()

    def getEntity(self, id):
        "Returns False if no entity was found."
        self._loadData()
        entityProperties = self.data[id]

        return Entity(id = id, properties = entityProperties, data_provider = self)
        try:
            entityProperties = self.data[id]
        except ValueError:
            return False
        
        return Entity(id = id, properties = entityProperties, data_provider = self)

    def saveEntity(self, entity):
        entity.data_provider = self
        if entity.id == None:
            #TODO: Generate an ID
            pass
        self.data[entity.id] = entity

        self._saveData()
        

        
    def create(self, properties = None):
        newEntity = Entity(properties = properties, data_provider = self)
        newEntity.save()
        return newEntity
    
    def retrieve(self, id):
        try:
            return self.data[id]
        except ValueError:
            return False
    
    def update(self, id, properties):
        editEntity = self.getEntity(id)
        editEntity = dict(properties)
        editEntity.save()
        return editEntity
    
    def delete(self, id):
        try:
            del self.data[id]
        except ValueError:
            return False
        
        return True

#TODO: SQLite provider


