# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# App title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on order
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake and read fruit options
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If user selected ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Get corresponding SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chosen + " Nutrition Information")

        # API request to get fruit nutrition
        try:
            response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on.lower())
            if response.status_code == 200:
                nutrition_df = pd.json_normalize(response.json())
                st.dataframe(nutrition_df, use_container_width=True)
            else:
                st.warning(f"Could not fetch nutrition info for {fruit_chosen} (status: {response.status_code})")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Submit order button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
        except Exception as e:
            st.error(f"Order failed to submit: {e}")
