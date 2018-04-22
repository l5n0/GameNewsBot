import discord

class GameNews(object):
	"""Represent a News object"""

	url         = None
	sourceName  = None
	title    	= None
	contents 	= None

	def __init__(self, url, sourceName, title, contents):
		self.url 		= url
		self.sourceName = sourceName
		self.title 		= title
		self.contents 	= contents

	def getEmbed(self, gameName):
		"""Transform this news object in a embed"""
		embed = discord.Embed(title=self.title, url=self.url, description=self.contents)
		embed.set_footer(text=self.sourceName)
		embed.set_author(name=gameName)
		return embed