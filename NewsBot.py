import discord
from discord.ext.commands import Bot
from discord.ext import commands

import asyncio

import datetime

from DataManager import DataManager
from SteamNewsFinder import SteamNewsFinder



# Constatnts
token = "TOKEN_ID"
newsChannel="channel_id"

bot_prefix="!"
fileName="gamenews.txt"	# File that will store all the news info.
frequency=600			# The frequency with which the bot checks news


# Variables
newsData 	= {}
dataManager = None


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


################ COMMANDS #######################


@bot.command(pass_context=True)
async def state(ctx):
	"""Print games that are currently in the list and their steam ids"""
	global newsData
	message = "Games on the list:\n"

	for game in newsData:
		message += " - " + game + " (" + str(newsData[game]['id']) + ")\n"
	
	await bot.send_message(bot.get_channel(newsChannel), message)

@bot.command(pass_context=False)
async def register(name, id):
	"""It allows user to register new games on the list"""
	global newsData

	newsData[name] = {}
	newsData[name]['name'] = name
	newsData[name]['id']   = id
	newsData[name]['news'] = []

	message = "Game with id '" + id + "' and name '" + name + "' has been registered. News will arrive in about 10 minutes."

	await bot.send_message(bot.get_channel(newsChannel), message)


###############   TASKS   ########################

async def getNews(gameName):
	global newsData

	game = newsData[gameName]
	print(game['name'])
	news = SteamNewsFinder.getGameNews(game['id'])
	counter = 0
	for newsItem in news:
		newsItemDict = newsItem.__dict__
		if (newsItemDict not in game['news']):
			counter+=1
			await bot.send_message(bot.get_channel(newsChannel), embed=newsItem.getEmbed(gameName))
			game['news'].append(newsItemDict)
	print("Done! " +  str(counter) + " news")

async def backgroundNewsSeeking():
	"""This task is supposed to be run in the background. It will update the news data and post new news in the news channel"""
	global newsData

	await asyncio.sleep(10) # 10 seconds delay
	await bot.wait_until_ready()
	while (1):
		print("Seeking for news ... -----------(" + str(datetime.datetime.now().time()) + ")")
		for game in newsData:
			await getNews(game)
		dataManager.saveData(newsData)
		print("News done!          -----------")
		await asyncio.sleep(frequency) 

bot.run(token)