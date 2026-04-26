import json 
import requests

from bs4 import BeautifulSoup


LEAGUE = "https://understat.com/league/EPL/2025"

response = requests.get(LEAGUE)
soup = BeautifulSoup(response.content, "lxml")
soup_scripts = soup.find_all("script")
print(type(soup_scripts))
print(soup_scripts)