import json
from dataprovider import DataProvider
from entity import Entity


class JSONDataProvider(DataProvider):
    """A dataprovider which is kept locally as a json file."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {}
        self.loaded = False
        self._loadData()

    def _saveData(self):
        """Save the data to our json file"""
        json_file = open(self.filepath, 'w+')
        json.dump(self.data, json_file)
        json_file.close()

    def _loadData(self):
        """Loads all data from the json copy."""
        try:
            myFile = open(self.filepath, 'r')
            self.data = json.load(myFile)
            myFile.close()
        except IOError:
            pass
            #TODO: Do we wana handle this at all?

    def createEntity(self, properties = None, key = None):
        """Create an entity in our database.  Returns an Entity.  If no key is present, a key will be generated."""
        return self.addEntity(Entity(properties = properties, key = key))

    def addEntity(self, entity = None):
        """Add an entity.  If no key is present, a key will be generated.  Returns the added Entity."""
        #TODO: THIS IS SLOOOOWWWWWWWW.  Filter, Sort, and Add
        keys = self.keys()
        myKey = 0
        
        while myKey in keys:
            myKey += 1
            
        entity.key = myKey
        
        entity.data_provider = self
        
        self[entity.key] = entity
        
        self._saveData()
        
        return entity #Needs to return entity so createEntity return it.
        

    def getEntity(self, key):
        """Returns False if no entity was found.  Loads the database if it has not been yet."""
        if not self.loaded:
            self._loadData()
        try:
            jsonEntity = self.data[key]
        except ValueError:
            return False
        
        entityProperties = jsonEntity
        return Entity(key = key, properties = entityProperties, data_provider = self)
    
    def getEntities(self):
        """Return many entities.  Will need a filter."""
        #TODO: Implement getEntities
        raise NotImplementedError
        

    def _saveEntity(self, entity):
        """Save a single entity.  Also saves the database."""
        entity.data_provider = self

        self.data[entity.key] = entity

        self._saveData()
        
    def _deleteEntity(self, entity):
        """Delete a single entity from the database.  Also saves the database."""
        del self[entity.key]
        self._saveData()