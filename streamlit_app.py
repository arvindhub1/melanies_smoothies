# Import Python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for Name on Order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Read fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect fruit choices
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Show nutrition info
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on.lower())
            if response.status_code == 200:
                nutrition_df = pd.json_normalize(response.json())
                st.dataframe(nutrition_df, use_container_width=True)
            else:
                st.warning(f"Could not fetch info for {fruit_chosen}")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Insert order into database
    time_to_insert = st.button('Submit order')

    if time_to_insert:
        try:
            insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_stmt).collect()
            st.success("Your Smoothie is ordered! ✅")
        except Exception as e:
            st.error(f"Order failed to submit: {e}")
