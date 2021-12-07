from bs4 import BeautifulSoup
import requests
import json

list_of_ids = []
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


with open('card_ids.json', 'w') as fout:
    json.dump(list_of_ids, fout)

    # if key == 'data':
    #     for x in key:
    #         for data_key, data_value in x.items():
    #             if data_key == 'id':
    #                 list_of_id.append(data_value)

# list_of_ids = []
# for key, value in data.items():
#     if key == 'data':
#         for x in key:
#             for data_key, data_value in x.items():
#                 if data_key == 'id':
#                     list_of_ids.append(data_value)

# print(list_of_ids[0])