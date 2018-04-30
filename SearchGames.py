from bs4 import BeautifulSoup
from urllib.request import urlopen

steamDbUrl = "https://store.steampowered.com/search/?page=@page@&term="

async def searchGames(searchtoken,page):
	result = []

	searchUrl = steamDbUrl.replace("@page@",str(page)) + searchtoken.replace(" ","%20")

	request    = urlopen(searchUrl)
	parsedHtml = BeautifulSoup(request.read(), "html.parser")

	searchResults = parsedHtml.body.find_all('a',"search_result_row")

	for r in searchResults:
		pair = {}
		rowTokens = r.get('href').split('/')
		pair['name'] = rowTokens[5].replace("_"," ")
		pair['id']   = rowTokens[4]
		pair['url']  = r.get('href')
		result.append(pair)

	return result
