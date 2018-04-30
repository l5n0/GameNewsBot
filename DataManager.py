import json

class DataManager(object):
	"""Encapsulate data storage in json files"""

	storageFileName = None

	def __init__(self, fileName):
		self.storageFileName = fileName

	def loadData(self):
		try:
			file = open(self.storageFileName,"r")
		except IOError:
			file = open(self.storageFileName,"w")
			file.close()
			file = open(self.storageFileName,"r")
		
		content = file.read()
		if (content == ""):
			return {}

		jsonObject = json.loads(content)
		file.close()
		return jsonObject

	def saveData(self, data):
		file = open(self.storageFileName, "w")
		file.write(json.dumps(data))
		file.close()