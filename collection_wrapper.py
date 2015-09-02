import pymongo
import threading
import pandas as pd

class CollectionWrapper:
	
	lock = None
	dbName = None
	collectionName = None
	collection = None
	def __init__(self, collName):
		self.lock = threading.Lock()
		self.dbName = 'quiverdb'
		self.collectionName = collName
		client = pymongo.MongoClient()
		db = client[self.dbName]
		self.collection = db[collName]

# data(DataFrame) -> X
	def store_dataframe(self, data):
		self.lock.acquire()
		dataDict = data.to_dict('records')
		self.collection.insert_many(dataDict)
		self.collection.create_index([('timestamp',pymongo.ASCENDING),('zone',pymongo.ASCENDING)])
		self.lock.release()

	def load_dataframe(self, query):
		self.lock.acquire()
		df = pd.DataFrame(list(self.collection.find(query)))
		self.lock.release()
		return df

	def pop_dataframe(self,query):
		self.lock.acquire()
		df = pd.DataFrame(list(self.collection.find(query)))
		self.lock.release()
		return df

	def remove_all(self):
		self.lock.acqure()
		self.collection.remove()
		self.lock.release()

