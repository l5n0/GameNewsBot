# GameNewsBot - A discord bot

This discord bot use steam news api to keep your discord channel updated with game news. The bot allows you to register the Steam app ids of your favorite games, checks periodically for games news and posts them on your Discord channel.


### Dependencies

**Python Libraries**:
 * discord.py
 * asyncio
 * datetime
 * json
 * html2text
 * urllib

### Configuration

 Go to NewsBot.py; you must set a value for:
 ```python
 token="CHANNEL BOT TOKEN"
 newsChannel="DISCORD CHANNEL ID"
 ```
 You can change the following values:
 ```python
 bot_prefix="!"
 fileName="gamenews.txt" # File that will store all the news info.
 ```
 
### Use

You can use [SteamDb](https://steamdb.info/) to check for Steam ids. And then say this on your *news channel*:
```
!register <gameName> <steamId>
```

**GameName must have no spaces**. For example:
```
!register CounterStrikeGO 730
```
Bot should response the following:
*Game with id '730' and name 'CounterStrikeGO' has been registered. News will arrive in about 10 minutes.*