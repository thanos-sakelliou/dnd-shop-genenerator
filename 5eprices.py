import pandas as pd
import numpy as np
import streamlit as st


###############################
SPELLCASTERS = ["Warlock", "Cleric", "Wizard", "Sorcerer", "Ranger"]
RARITIES = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary', 'Artifact']
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
    return int(better_price)

def price_fluctuation(row):
    random_variance = np.random.randint(low=-row['Suggested Price']/20-1, high=row['Suggested Price']/20)*10
    return  '{0:+d}'.format(random_variance) 

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
        if "Level" in row['Item']: 
            spell_level = int(row['Item'].split("Level ")[1][0])
            sp = generate_spell(level=spell_level, spellcasters=spellcasters)
            new_name = name + sp.name.iloc[0]
            return new_name
        else:
            return row['Item']

    items['Item'] = items.apply(add_spell, axis=1)
    return items

######MAIN#################

def split_and_sample_items(relevant_items, equipment_items_number, mage_items_number, consumable_items_number, health_potion_items_number, scroll_items_number):
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
    populate_with_spells(mage_items, [], "Wand Of ")

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

    return sampled_consumable_items, sampled_equipment_items, sampled_mage_items

def load_items(df):
    #filter with prices
    relevant_items = df[df['DMPG Price'].notnull()]

    # #add new prices
    relevant_items.insert(1, 'Suggested Price', 0)
    relevant_items['Suggested Price'] = relevant_items.apply(better_price, axis=1)
    relevant_items.insert(2, 'Fluctuation', 0)
    relevant_items['Fluctuation'] = relevant_items.apply(price_fluctuation, axis=1)
    return relevant_items

def export_to_excel(sampled_consumable_items, sampled_equipment_items, sampled_mage_items):
    with pd.ExcelWriter('output.xlsx') as writer:  
        sampled_consumable_items.to_excel(writer, sheet_name='Consumables')
        sampled_equipment_items.to_excel(writer, sheet_name='Equipment')
        sampled_mage_items.to_excel(writer, sheet_name='Mage items')

def style_options():
    st.markdown( 
    """<style>
        .stDataFrame div {text-align: left !important}
    </style>
    """, unsafe_allow_html=True) 

#TODO
#ratio use
#intergation 5e.tools
#5e.tools links
#GUI refinement

#KNOWNFAULTS
#spellists select all possible subclasses

#------------------------MAIN-----------------------------------------

st.title('5e Magic Shop Items Generator')

col1, col2 = st.beta_columns([1,3])
cont1 = st.beta_container()
cont2 = st.beta_container()
cont3 = st.beta_container()
style_options()

with st.beta_container():
    basic_rarity_id = st.selectbox("Items basic rarity", options=[0,1,2,3,4,5], index=1, format_func=lambda o:RARITIES[o], help=None)

with col1:
    st.write("------------")
    spellcasters = st.multiselect("Spellcaster classes for scrolls", SPELLCASTERS, default=None)
    selected_rarities = [RARITIES[i] for i in range(basic_rarity_id+1)]
    consumable_items_number = st.slider("Consumables number", min_value=0, max_value=20, value=5, step=1)
    health_potion_items_number = st.slider("Health potions number", min_value=0, max_value=20, value=5, step=1)
    scroll_items_number = st.slider("Scrolls number", min_value=0, max_value=20, value=5, step=1)
    st.write("------------")
    equipment_items_number = st.slider("Equipment & wondrous items number", min_value=0, max_value=20, value=8, step=1)
    st.write("------------")
    mage_items_number = st.slider("Spellcaster items number", min_value=0, max_value=20, value=5, step=1)



df = pd.read_excel(("D&D Magical Item Prices.xlsx"))
df.drop(['DMG Price'], axis=1)
# print(list(df['Rarity'].unique()))
relevant_items = load_items(df)
sampled_consumable_items, sampled_equipment_items, sampled_mage_items = split_and_sample_items(relevant_items, equipment_items_number, mage_items_number, consumable_items_number, health_potion_items_number, scroll_items_number)


with col2:
    st.header("Consumables")
    st.dataframe(sampled_consumable_items, height=500)

    st.header("Equipment and Wondrous Items")
    st.dataframe(sampled_equipment_items)

    st.header("Spellcaster Items")
    st.dataframe(sampled_mage_items)

    