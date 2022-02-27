import requests
import json
import logging

def load_cards():
    """Load card data from the API to a local json file titled "card_data.json"
    """
    list_of_card_info = []
    num = 1
    while num < 59:
        # Connect to API
        BASE_URL = f'https://api.pokemontcg.io/v2/cards/?search=a&page={num}'
        request = requests.get(BASE_URL)
        data = request.json()

        # Collect data
        for key, value in data.items():
            if key == 'data':
                for dicts in value:
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
                    list_of_card_info.append(dict_of_card_info)
        num += 1

    # Write data to local file
    with open('API/card_data.json', 'w') as fout:
        json.dump(list_of_card_info, fout)

    logging.basicConfig(filename='cardagain.log', level=logging.DEBUG, format='[%(asctime)s %(levelname)s] %(funcName)s - %(message)s')
    logging.debug('Looks fine.')


# For loading the data
# with open('API/card_ids.json', 'r') as fin:
#     ids = json.load(fin)

# Run the function
load_cards()

