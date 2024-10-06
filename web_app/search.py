# Utils
from root_config import *
from utils import *

# Modules 
import requests
from selectolax.parser import HTMLParser
# ===================================================================== #

class Search:
    def __init__(self, search_key: str) -> None:
        self.search_key = search_key.replace(" ", "-")

    def search(self) -> list[dict]:
        search_query = f"{BASE_URL}/search/{self.search_key}"
        results_page = HTMLParser(requests.get(search_query).content)
        items = results_page.css("div.flw-item")
        
        results = []
        for item in items:
            try:
                details = dict()
                details["name"] = item.css_first("h2.film-name").text(strip=True)
                details["year"] = item.css_first("span.fdi-item").text(strip=True)
                details["image"] = item.css_first("img").attributes["data-src"]
                details["quality"] = item.css_first("div.film-poster-quality").text(strip=True)
                details["url"] = BASE_URL + item.css_first("a").attributes["href"]
                details["type"] = item.css_first("span.fdi-type").text(strip=True)
                details["duration"] = item.css("span.fdi-item")[1].text(strip=True)
                results.append(details)
            except:
                pass
        
        return results
# --------------------------------------------------------------------- #