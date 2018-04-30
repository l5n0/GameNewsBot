import discord
from discord.ext.commands import Bot
from discord.ext import commands

import asyncio

import datetime

from threading import Thread, Lock

from DataManager     import DataManager
from SteamNewsFinder import SteamNewsFinder
from SearchGames     import searchGames


# Constatnts
token = "BOT_TOKEN"
newsChannel="CHANNEL_ID"

bot_prefix="!"
fileName="gamenews.txt"	# File that will store all the news info.
frequency=600			# The frequency with which the bot checks news


# Variables
newsDataMutex = Lock()
newsData 	= {}
dataManager = None
embedNews	= []	# Queue with news waiting to be posted in the news channel
lastSearch  = []

bot = commands.Bot(command_prefix=bot_prefix)

@bot.event
async def on_ready():
		global dataManager
		global newsData
		# Initialize variables
		print("Bot Online!")
		print("Initializating...")
		dataManager = DataManager(fileName)
		print("Loading news data... Storage: " + fileName)
		newsData = dataManager.loadData()
		print("Ready!")
		bot.loop.create_task(backgroundNewsSeeking())
		bot.loop.create_task(backgroundNewsSender())

################ REAL COMMANDS #######################

@bot.command(pass_context=False)
async def search(searchToken):
	global lastSearch

	result = await searchGames(searchToken,1)

	embed = discord.Embed(title="Resultados de la búsqueda '" + searchToken + "'")

	i = 0
	for r in result:
		embed.add_field(name= str(i) + ". " + r['name'], value="[Página de steam](" + r['url'] + ")")
		i = i+1

	lastSearch = result

	await bot.send_message(bot.get_channel(newsChannel), embed=embed)


@bot.command(pass_context=False)
async def state():
	"""Print games that are currently in the list and their steam ids"""
	global newsData
	message = "Games on the list:\n"

	for game in newsData:
		message += " - " + game + " (" + str(newsData[game]['id']) + ")\n"
	
	await bot.send_message(bot.get_channel(newsChannel), message)

@bot.command(pass_context=False)
async def register(number):
	global newsData
	global lastSearch

	if (lastSearch == []):
		await bot.send_message(bot.get_channel(newsChannel), "Search something first! Don't use spaces on your search. There is an example:\n !search Hollow_Knight")
		return

	if (int(number) < 0 ):
		await bot.send_message(bot.get_channel(newsChannel), "Please enter a valid search number.")
		return

	try:
		name     = lastSearch[int(number)]['name']
		gameId   = lastSearch[int(number)]['id']
	except IndexError:
		await bot.send_message(bot.get_channel(newsChannel), "Please enter a valid search number.")
		return

	newsData[name] = {}
	newsData[name]['name'] = name
	newsData[name]['id']   = gameId
	newsData[name]['news'] = []

	newsDataMutex.acquire()
	try:
		dataManager.saveData(newsData)
	finally:
		newsDataMutex.release()

	message = "Game with id '" + gameId + "' and name '" + name + "' has been registered."

	await bot.send_message(bot.get_channel(newsChannel), message)
	Thread(target = getNews, args = (name,)).start()



###############   TASKS   ########################

def getNews(gameName):
	"""Check for new news, add them to embedNews, and update newsData. Multi-threading."""
	global newsData

	game = newsData[gameName]
	news = SteamNewsFinder.getGameNews(game['id'])
	counter = 0
	for newsItem in news:
		newsItemDict = newsItem.__dict__
		if (newsItemDict not in game['news']):
			counter+=1
			embedNews.append(newsItem.getEmbed(gameName))
			game['news'].append(newsItemDict)
	newsDataMutex.acquire()
	try:
		dataManager.saveData(newsData)
	finally:
		newsDataMutex.release()
	print(gameName + " Done! " +  str(counter) + " news")

async def backgroundNewsSeeking():
	"""This task is supposed to be run in the background. It will update the news data"""
	global newsData

	await asyncio.sleep(5) # 10 seconds delay
	await bot.wait_until_ready()
	while (1):
		print("\nSeeking for news ... -----------(" + str(datetime.datetime.now().time()) + ")")
		for game in newsData:
			Thread(target = getNews, args = (game,)).start()
		await asyncio.sleep(600)

async def backgroundNewsSender():
	"""This task is supposed to be run in the background. Check for news and posts it in the news channel"""
	global embedNews
	while(1):
		if embedNews:
			for embed in embedNews:
				await bot.send_message(bot.get_channel(newsChannel), embed=embedNews.pop())
		await asyncio.sleep(5)

bot.run(token)