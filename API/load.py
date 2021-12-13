from bs4 import BeautifulSoup
import requests
import json
import time

list_of_ids = []
dict_of_important_card_information = {}
num = 1
while num < 59:
    BASE_URL = f'https://api.pokemontcg.io/v2/cards/?search=a&page={num}'
    request = requests.get(BASE_URL)
    data = request.json()
    for key, value in data.items():
        if key == 'data':
            for dicts in value:
                for key_data, value_data in dicts.items():
                    if key_data == 'id':
                        list_of_ids.append(value_data)
    num += 1


with open('API/card_ids.json', 'r') as fin:
    ids = json.load(fin)

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

