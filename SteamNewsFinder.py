import json
from urllib.request import urlopen
from GameNews import GameNews

import html2text

idPlaceholder = "#GAMEID#"
steamNewsUrl = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=" + idPlaceholder + "&count=3&maxlength=300&format=json"

class SteamNewsFinder(object):
	"""Encapsulate the behaviour from game news seeking"""

	@staticmethod
	def getGameNews(steamId):
		"""Make the request for news to Steam api and transform the response into GameNews objects."""
		news = []

		url 	= steamNewsUrl.replace(idPlaceholder, str(steamId))
		response = urlopen(url)
		contentObject = json.loads(response.read()) 
		for noticia in contentObject["appnews"]["newsitems"]:
			urlSteam = noticia["url"]
			urlReal  = urlopen(urlSteam).url
			source   = noticia["feedlabel"]
			title    = noticia["title"]
			contents = html2text.html2text(noticia["contents"])

			newsItem = GameNews(urlReal, source, title, contents)
			news.append(newsItem)

		return news