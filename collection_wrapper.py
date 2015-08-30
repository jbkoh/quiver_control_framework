import pymongo
import pandas as pd

class CollectionWrapper:
	
	dbName = None
	collectionName = None
	collection = None
	def __init__(self, collName):
		self.dbName = 'quiverdb'
		self.collectionName = collName
		client = pymongo.MongoClient()
		db = client[self.dbName]
		self.collection = db[collName]

# data(DataFrame) -> 
	def store_dataframe(self, data):
		dataDict = data.to_dict('records')
		self.collection.insert_many(dataDict)
		self.collection.create_index([('timestamp',pymongo.ASCENDING),('zone',pymongo.ASCENDING)])

	def load_dataframe(self, query):
		df = pd.DataFrame(list(self.collection.find(query)))
		return df

	def remove_all(self):
		self.collection.remove()
