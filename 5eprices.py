import pandas as pd
import numpy as np


selected_rarities =  ['Common','Uncommon']
spellcasters = ["Warlock", "Cleric"]
equipment_items_number = 8
mage_items_number = 5
consumable_items_number = 5
health_potion_items_number = 5
scroll_items_number = 5

df = pd.read_excel(("D&D Magical Item Prices.xlsx"))

###############################
RARITIES = ['Very Rare', 'Rare', 'Uncommon', 'Artifact', 'Varies', 'Legendary', 'Common']
SOURCES = ['ID', 'TCE', 'EGW', 'DMG', 'MOoT', 'TYP', 'TA', 'BR', 'EBR', 'UA', 'WGE', 'XGE', 'WDH', 'PA', 'SKT',
           'BGA', 'DMM', 'HDQ', 'LLK', 'CS', 'RT', 'SDW', 'AI', 'GoS', 'OA', 'LMP', 'DC', 'MTF', 'GGR', 'TH', 'VGM', 'HT']
TYPES = ['Wondrous Items', 'Weapons', 'Armor', 'Ammunition', 'Wondrous Items: Neck', 'Wondrous Item', 'Shields', 'Wands', 'Rings', 'Ring', 'Wondrous Items: Waist', 'Wondrous Items: Eyes', 'Staffs', 'Rods', 'Wondrous Items: Feet',
         'Potions & Oils', 'Wondrous Items: Arms & Wrists', 'Wondrous Items: Head', 'Wondrous Items: Shoulders', 'Wondrout Items', 'Wondrous Items: Hands', 'Wondrous Items: Body', 'Potion', 'Spell Scrolls', 'Spell Gems']
CONSUMABLE = ['Potions & Oils', 'Ammunition', 'Potion', 'Spell Scrolls', 'Spell Gems']
EQUIPMENT = ['Wondrous Items', 'Weapons', 'Armor', 'Wondrous Items: Neck', 'Wondrous Item', 'Shields', 'Rings', 'Ring', 'Wondrous Items: Waist', 'Wondrous Items: Eyes',
             'Wondrous Items: Feet', 'Wondrous Items: Arms & Wrists', 'Wondrous Items: Head', 'Wondrous Items: Shoulders', 'Wondrout Items', 'Wondrous Items: Hands', 'Wondrous Items: Body']
MAGE = ['Wands', 'Staffs', 'Rods']
#####################################

def better_price(row):
    dmpg_price = int(row['DMPG Price'])
    better_price = dmpg_price*2
    
    #use sane
    try:
        sane_price = int(row['Sane Price'])
        if better_price >= sane_price:
            better_price = sane_price
        else:
            ratio = sane_price / better_price
    except: True

    random_variance = np.random.randint(low=-dmpg_price/20-1, high=dmpg_price/20)*10
    return str(better_price) + " (" + '{0:+d}'.format(random_variance) + ")"

def multiple_occurances(items, number):
    items = items.sample(n=number, replace=True)
    occ =  pd.DataFrame(items['Item'].value_counts()).reset_index()
    occ.columns = ['Item', 'counts']
    items.drop_duplicates(inplace=True)
    items.reset_index(drop=True, inplace=True)
    items['Item'] = items['Item'].astype(str) + " x" + occ['counts'].astype(str)
    return items

def generate_spell(level, spellcasters=[]):
    spells = pd.read_json("spells.json")
    spells = spells[spells.level == level]
    if spellcasters:
        regex_classes = (''.join([str(e)+'|' for e in spellcasters]))[:-1]
        spells = spells[spells['classes'].map(str).str.contains(regex_classes, regex=True, na=False)]
    return spells.sample(n=1)

def populate_with_spells(items, spellcasters=[], name="Scroll of "):

    def add_spell(row):
        # spell_level = row['Item'].str.extract(r'([Level ])(\d)')[1].map(int)
        spell_level = int(row['Item'].split("Level ")[1][0])
        sp = generate_spell(level=spell_level, spellcasters=spellcasters)
        new_name = name + sp.name.iloc[0]
        return new_name

    items['Item'] = items.apply(add_spell, axis=1)
    return items

######MAIN#################


# print(list(df['Rarity'].unique()))

#filter with prices
relevant_items = df[df['DMPG Price'].notnull()]

#add new prices
relevant_items.insert(1, 'Suggested Price', 0)
relevant_items['Suggested Price'] = relevant_items.apply(better_price, axis=1)

print(relevant_items)

#split to categories
consumable_items = relevant_items[relevant_items['Type'].isin(CONSUMABLE)]
consumable_items = consumable_items[consumable_items['Rarity'].isin(selected_rarities)]
health_potion_items = consumable_items[consumable_items['Item'].str.contains('Potion Of Healing', na=False)]
scroll_items = consumable_items[consumable_items['Type'] == 'Spell Scrolls']
consumable_items = consumable_items[~consumable_items['Item'].str.contains('Potion Of Healing', na=False)]
consumable_items = consumable_items[~(consumable_items['Type'] == 'Spell Scrolls')]

equipment_items = relevant_items[relevant_items['Type'].isin(EQUIPMENT)]
equipment_items = equipment_items[equipment_items['Rarity'].isin(selected_rarities)]

mage_items = relevant_items[relevant_items['Type'].isin(MAGE)]
mage_items = mage_items[mage_items['Rarity'].isin(selected_rarities)]


#sample number of items
sampled_consumable_items = consumable_items.sample(n=consumable_items_number, replace=True)

# multiple occurances of health potions
sampled_health_potion_items = multiple_occurances(health_potion_items, health_potion_items_number)

#sampled scrolls with spells
sampled_scroll_items = scroll_items.sample(n=scroll_items_number, replace=True)
populate_with_spells(sampled_scroll_items, spellcasters)

#add to consumables
sampled_consumable_items = sampled_consumable_items.append(sampled_health_potion_items)
sampled_consumable_items = sampled_consumable_items.append(sampled_scroll_items)

sampled_equipment_items = equipment_items.sample(n=equipment_items_number)

sampled_mage_items = mage_items.sample(n=mage_items_number)


#export
with pd.ExcelWriter('output.xlsx') as writer:  
    sampled_consumable_items.to_excel(writer, sheet_name='Consumables')
    sampled_equipment_items.to_excel(writer, sheet_name='Equipment')
    sampled_mage_items.to_excel(writer, sheet_name='Mage items')


#TODO
#quantity
#standard potions
#ratio use

#KNOWNFAULTS
#spellists select all possible subclasses