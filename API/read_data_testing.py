# Testing reading from card_data.json file

import json

with open('API/card_data.json', 'r') as fin:
    card_data = json.load(fin)

print(card_data[1]['set_name'])
print(card_data[1]['set_series'])