import json

with open('API/card_data.json', 'r') as fin:
    card_data = json.load(fin)

print(float(card_data[0]['price']['holofoil']['low']))

# for info in card_data:
#     try:
#         if info['price']['normal']['low']:
#             normal_price_low = info['price']['normal']['low']
#         pass
#     except:
#         pass
# print(normal_price_low)