# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# User input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If ingredients selected
if ingredients_list:
    # Create ingredient string in correct format
    ingredients_string = ', '.join(ingredients_list)

    # Show nutrition info for each fruit
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Build insert SQL
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button('Submit order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('✅ Your Smoothie is ordered!')
