
from DataProvider import dataprovider  # @UnresolvedImport

dp = dataprovider.JSONDataProvider('test.json')
myEntity = dataprovider.Entity(
        id          = 'test', 
        properties  = {
                'a': '1', 
                'b': '2'
            }
    )

#dp.saveEntity(myEntity)

#print myEntity

newEntity = dp.getEntity('test')
print newEntity

