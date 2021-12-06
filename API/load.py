from bs4 import BeautifulSoup
import requests
import json

BASE_URL = f'https://api.pokemontcg.io/v2/cards'
# id = 'xy5-1'
request = requests.get(BASE_URL)
data = request.json()

list_of_ids = []
for key, value in data.items():
    if key == 'data':
        for x in key:
            for data_key, data_value in x.items():
                if data_key == 'id':
                    list_of_ids.append(data_value)

print(list_of_ids[0])