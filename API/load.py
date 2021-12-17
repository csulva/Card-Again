from bs4 import BeautifulSoup
import requests
import json
import time

list_of_all_information = []
list_of_card_info = []
num = 1
while num < 59:
    BASE_URL = f'https://api.pokemontcg.io/v2/cards/?search=a&page={num}'
    request = requests.get(BASE_URL)
    data = request.json()
    for key, value in data.items():
        if key == 'data':
            for dicts in value:
                # for x in dicts:
                dict_of_card_info = {}
                dict_of_card_info['id'] = dicts['id']
                dict_of_card_info['name'] = dicts['name']
                try:
                    if dicts['rarity']:
                        dict_of_card_info['rarity'] = dicts['rarity']
                except:
                    dict_of_card_info['rarity'] = None
                try:
                    if dicts['nationalPokedexNumbers']:
                        dict_of_card_info['pokedex_number'] = dicts['nationalPokedexNumbers'][0]
                except:
                    dict_of_card_info['pokedex_number'] = None
                dict_of_card_info['image'] = dicts['images']['small']
                try:
                    if dicts['set']:
                        dict_of_card_info['set_name'] = dicts['set']['name']
                        dict_of_card_info['set_series'] = dicts['set']['series']
                except:
                    dict_of_card_info['set_name'] = None
                    dict_of_card_info['set_series'] = None
                try:
                    if dicts['tcgplayer']['url']:
                        dict_of_card_info['url'] = dicts['tcgplayer']['url']
                except:
                    dict_of_card_info['url'] = None
                try:
                    if dicts['tcgplayer']['updatedAt']:
                        dict_of_card_info['last_updated'] = dicts['tcgplayer']['updatedAt']
                except:
                    dict_of_card_info['last_updated'] = None
                try:
                    if dicts['tcgplayer']['prices']:
                        dict_of_card_info['price'] = dicts['tcgplayer']['prices']
                except:
                    dict_of_card_info['price'] = None
                # try:
                #     if dicts['tcgplayer']['prices']['normal']:
                #         dict_of_card_info['low_price'] = dicts['tcgplayer']['prices']['normal']['low']
                # except:
                #     if dicts['tcgplayer']['prices']['holofoil']:
                #         dict_of_card_info['low_price'] = dicts['tcgplayer']['prices']['holofoil']['low']
                #         # dict_of_card_info['mid_price'] = dicts['tcgplayer']['prices']['holofoil']['mid'] or dicts['tcgplayer']['prices']['normal']['mid']
                #         # dict_of_card_info['high_price'] = dicts['tcgplayer']['prices']['holofoil']['high'] or dicts['tcgplayer']['prices']['normal']['high']
                #         # dict_of_card_info['market_price'] = dicts['tcgplayer']['prices']['holofoil']['market'] or dicts['tcgplayer']['prices']['normal']['market']
                # else:
                #     dict_of_card_info['low_price'] = None
                list_of_card_info.append(dict_of_card_info)
            # list_of_all_information.append(list_of_card_info)
    num += 1

with open('API/card_data.json', 'w') as fout:
    json.dump(list_of_card_info, fout)

# with open('API/card_ids.json', 'r') as fin:
#     ids = json.load(fin)

# BASE_URL = f'https://api.pokemontcg.io/v2/cards/{id}'
# request = requests.get(BASE_URL)
# card_data = request.json()

# For ID,
# def get_api_items_first_level(card_ids, api_key):
#     data_list = []
#     for id in card_ids:
#         BASE_URL = f'https://api.pokemontcg.io/v2/cards/{id}'
#         request = requests.get(BASE_URL)
#         card_data = request.json()
#         for key, value in card_data.items():
#             if key == 'data':
#                 for key_data, value_data in value.items():
#                     if key_data == api_key:
#                         data_list.append(value_data)
#     return data_list


# data_list = []
# index = 0
# for id in ids:
#     BASE_URL = f'https://api.pokemontcg.io/v2/cards/' + id
#     request = requests.get(BASE_URL)
#     request.raise_for_status()
#     if request.status_code != 204:
#         card_data = request.json()
#         for key, value in card_data.items():
#             if key == 'data':
#                 for key_data, value_data in value.items():
#                     if key_data == 'id':
#                         data_list.append(value_data)
#     index += 1
#     if index == 100:
#         time.sleep(30)
#     if index == 200:
#         time.sleep(30)
#     if index == 300:
#         time.sleep(30)
#     if index == 400:
#         time.sleep(30)
#     if index == 500:
#         time.sleep(30)
#     if index == 600:
#         time.sleep(30)
#     if index == 700:
#         time.sleep(30)
#     if index == 800:
#         time.sleep(30)
#     if index == 900:
#         time.sleep(30)
#     if index == 1000:
#         time.sleep(30)
#     if index == 1100:
#         time.sleep(30)
#     if index == 1200:
#         time.sleep(30)

# print(len(data_list))

# print(get_api_items_first_level(ids, 'id'))
# index = 0
# while index <= len(data):
#     for id in data:
#         BASE_URL = f'https://api.pokemontcg.io/v2/cards/{id}'
#         request = requests.get(BASE_URL)
#         card_data = request.json()

