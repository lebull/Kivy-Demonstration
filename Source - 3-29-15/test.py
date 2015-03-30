
from DataProvider import dataprovider  # @UnresolvedImport

dp = dataprovider.JSONDataProvider('test.json')

myEntity = dataprovider.Entity(
        key          = 'test',
        data_provider = dp,
        properties  = {
                'a': [1, 2, 3], 
                'b': 2
            }
    )

subEntity = dataprovider.Entity(
        key          = 'subEntity', 
        properties  = {
                'a': 1, 
                'b': 2
            }
    )

myEntity['sub'] = subEntity

print myEntity.sub

myEntity.save()

#print dp.getEntity('test').sub

