import pandas as pd
import numpy as np


selected_rarities =  ['common','Uncommon']
equipment_items_number = 8
mage_items_number = 5
consumable_items_number = 15

###############################
RARITIES = ['Very Rare', 'Rare', 'Uncommon', 'Artifact', 'Varies', 'Legendary', 'Common']
SOURCES = ['ID', 'TCE', 'EGW', 'DMG', 'MOoT', 'TYP', 'TA', 'BR', 'EBR', 'UA', 'WGE', 'XGE', 'WDH', 'PA', 'SKT',
           'BGA', 'DMM', 'HDQ', 'LLK', 'CS', 'RT', 'SDW', 'AI', 'GoS', 'OA', 'LMP', 'DC', 'MTF', 'GGR', 'TH', 'VGM', 'HT']
TYPES = ['Wondrous Items', 'Weapons', 'Armor', 'Ammunition', 'Wondrous Items: Neck', 'Wondrous Item', 'Shields', 'Wands', 'Rings', 'Ring', 'Wondrous Items: Waist', 'Wondrous Items: Eyes', 'Staffs', 'Rods', 'Wondrous Items: Feet',
         'Potions & Oils', 'Wondrous Items: Arms & Wrists', 'Wondrous Items: Head', 'Wondrous Items: Shoulders', 'Wondrout Items', 'Wondrous Items: Hands', 'Wondrous Items: Body', 'Potion', 'Spell Scrolls', 'Spell Gems']
CONSUMABLE = ['Potions & Oils', 'Ammunition',
              'Potion', 'Spell Scrolls', 'Spell Gems']
EQUIPMENT = ['Wondrous Items', 'Weapons', 'Armor', 'Wondrous Items: Neck', 'Wondrous Item', 'Shields', 'Rings', 'Ring', 'Wondrous Items: Waist', 'Wondrous Items: Eyes',
             'Wondrous Items: Feet', 'Wondrous Items: Arms & Wrists', 'Wondrous Items: Head', 'Wondrous Items: Shoulders', 'Wondrout Items', 'Wondrous Items: Hands', 'Wondrous Items: Body']
MAGE = ['Wands', 'Staffs', 'Rods']
#####################################

df = pd.read_excel(
    ("D:/ARCHIVE/Documents/5eprices/D&D Magical Item Prices.xlsx"))

# print(list(df['Rarity'].unique()))

#filter with prices
relevant_items = df[df['DMPG Price'].notnull()]

#add new prices
relevant_items.insert(1, 'Suggested Price', 0)
relevant_items['Suggested Price'] = relevant_items.apply(
    lambda row: str(int(row['DMPG Price']*2)) + " +(" + str(np.random.randint(low=-row['DMPG Price']/20-1, high=row['DMPG Price']/20)*10) + ")",
    axis=1)

print(relevant_items)

#split to categories
consumable_items = relevant_items[relevant_items['Type'].isin(CONSUMABLE)]
consumable_items = consumable_items[consumable_items['Rarity'].isin(selected_rarities)]

equipment_items = relevant_items[relevant_items['Type'].isin(EQUIPMENT)]
equipment_items = equipment_items[equipment_items['Rarity'].isin(selected_rarities)]

mage_items = relevant_items[relevant_items['Type'].isin(MAGE)]
mage_items = mage_items[mage_items['Rarity'].isin(selected_rarities)]

sampled_consumable_items = consumable_items.sample(n=consumable_items_number)
sampled_equipment_items = equipment_items.sample(n=equipment_items_number)
sampled_mage_items = mage_items.sample(n=mage_items_number)



with pd.ExcelWriter('output.xlsx') as writer:  
    sampled_consumable_items.to_excel(writer, sheet_name='Consumables')
    sampled_equipment_items.to_excel(writer, sheet_name='Equipment')
    sampled_mage_items.to_excel(writer, sheet_name='Mage items')