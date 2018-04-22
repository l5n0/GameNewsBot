import json

class DataManager(object):
	"""Encapsulate data storage in json files"""

	storageFileName = None

	def __init__(self, fileName):
		self.storageFileName = fileName

	def loadData(self):
		file = open(self.storageFileName,"r")
		jsonObject = json.loads(file.read())
		file.close()
		return jsonObject

	def saveData(self, data):
		file = open(self.storageFileName, "w")
		file.write(json.dumps(data))
		file.close()