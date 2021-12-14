import json

with open('API/card_data.json', 'r') as fin:
    card_data = json.load(fin)

print(card_data[5002])