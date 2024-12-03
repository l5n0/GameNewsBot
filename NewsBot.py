import discord
from discord.ext import commands
import asyncio
import datetime
from threading import Thread, Lock
from DataManager import DataManager
from SteamNewsFinder import SteamNewsFinder
from SearchGames import searchGames
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants loaded from the .env file
token = os.getenv("DISCORD_TOKEN")
newsChannel = os.getenv("NEWS_CHANNEL_ID")
bot_prefix = "!"
fileName = "gamenews.txt"  # File that will store all the news info.
frequency = 600  # The frequency with which the bot checks news

# Variables
newsDataMutex = Lock()
newsData = {}
dataManager = None
embedNews = []  # Queue with news waiting to be posted in the news channel
lastSearch = []

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent if needed

# Create the bot with the specified intents
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

@bot.event
async def on_ready():
    global dataManager
    global newsData
    # Initialize variables
    print("Bot Online!")
    print("Initializing...")
    dataManager = DataManager(fileName)
    print("Loading news data... Storage: " + fileName)
    newsData = dataManager.loadData()
    print("Ready!")
    bot.loop.create_task(backgroundNewsSeeking())
    bot.loop.create_task(backgroundNewsSender())

################ REAL COMMANDS #######################

@bot.command(pass_context=False)
async def search(ctx, searchToken):
    global lastSearch

    result = await searchGames(searchToken, 1)

    embed = discord.Embed(title="Search results for '" + searchToken + "'")

    i = 0
    for r in result:
        embed.add_field(name=str(i) + ". " + r['name'], value="[Steam Page](" + r['url'] + ")")
        i += 1

    lastSearch = result

    await ctx.send(embed=embed)

@bot.command(pass_context=False)
async def state(ctx):
    """Print games that are currently in the list and their steam ids"""
    global newsData
    message = "Games on the list:\n"

    for game in newsData:
        message += " - " + game + " (" + str(newsData[game]['id']) + ")\n"

    await ctx.send(message)

@bot.command(pass_context=False)
async def register(ctx, number: str):
    global newsData
    global lastSearch

    if not lastSearch:
        await ctx.send("Search something first! Don't use spaces in your search. Example:\n !search Hollow_Knight")
        return

    try:
        index = int(number)
        if index < 0 or index >= len(lastSearch):
            raise ValueError("Index out of range.")
        
        name = lastSearch[index]['name']
        gameId = lastSearch[index]['id']
        
    except ValueError:
        await ctx.send("Please enter a valid search number (e.g., !register 0).")
        return
    except IndexError:
        await ctx.send("Please enter a valid search number within range.")
        return

    newsData[name] = {'name': name, 'id': gameId, 'news': []}

    with newsDataMutex:
        dataManager.saveData(newsData)

    message = f"Game with id '{gameId}' and name '{name}' has been registered."
    
    await ctx.send(message)
    
    Thread(target=getNews, args=(name,)).start()

###############   TASKS   ########################

def getNews(gameName):
    """Check for new news, add them to embedNews, and update newsData. Multi-threading."""
    global newsData

    game = newsData[gameName]
    news_items = SteamNewsFinder.getGameNews(game['id'])
    
    counter = 0
    for newsItem in news_items:
        newsItemDict = newsItem.__dict__
        if newsItemDict not in game['news']:
            counter += 1
            embedNews.append(newsItem.getEmbed(gameName))
            game['news'].append(newsItemDict)
    
    with newsDataMutex:
        dataManager.saveData(newsData)
    
    print(f"{gameName} Done! {counter} new(s)")

async def backgroundNewsSeeking():
    """This task is supposed to be run in the background. It will update the news data"""
    global newsData

    await asyncio.sleep(5)  # Initial delay
    await bot.wait_until_ready()
    
    while True:
        print(f"\nSeeking for news ... -----------({datetime.datetime.now().time()})")
        
        for game in newsData:
            Thread(target=getNews, args=(game,)).start()
        
        await asyncio.sleep(frequency)

async def backgroundNewsSender():
    """This task is supposed to be run in the background. Check for news and posts it in the news channel"""
    global embedNews
    
    while True:
        if embedNews:
            while embedNews:
                embed = embedNews.pop(0)
                channel = bot.get_channel(int(newsChannel))
                if channel:
                    await channel.send(embed=embed)
        
        await asyncio.sleep(5)

bot.run(token)
