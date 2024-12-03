import json
import urllib.request
from urllib.parse import quote
from GameNews import GameNews
import html2text

idPlaceholder = "#GAMEID#"
steamNewsUrl = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=" + idPlaceholder + "&count=3&maxlength=300&format=json"

class SteamNewsFinder(object):
    """Encapsulate the behaviour from game news seeking"""

    @staticmethod
    def getGameNews(steamId):
        """Make the request for news to Steam API and transform the response into GameNews objects."""
        news = []

        # Construct the URL for Steam API
        url = steamNewsUrl.replace(idPlaceholder, str(steamId))
        
        # Define headers to mimic a browser request
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        try:
            # Make a request to the Steam API
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                contentObject = json.loads(response.read())
            
            # Process each news item in the response
            for noticia in contentObject["appnews"]["newsitems"]:
                urlSteam = noticia["url"]
                encoded_urlSteam = quote(urlSteam, safe=':/')
                
                # Follow any redirects to get the real URL
                req_real = urllib.request.Request(encoded_urlSteam, headers=headers)
                urlReal = urllib.request.urlopen(req_real).url
                
                source = noticia["feedlabel"]
                title = noticia["title"]
                contents = html2text.html2text(noticia["contents"])

                newsItem = GameNews(urlReal, source, title, contents)
                news.append(newsItem)

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e.msg}")

        return news

# Example usage:
if __name__ == "__main__":
    steam_id = 1142710  # Example Steam ID for Total War: WARHAMMER III
    news_items = SteamNewsFinder.getGameNews(steam_id)
    
    for item in news_items:
        print(item.format_news())
