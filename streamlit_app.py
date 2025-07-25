# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit data
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Multiselect fruit choices
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If fruits selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen]

        if not row.empty and pd.notna(row.iloc[0]['SEARCH_ON']):
            search_on = row.iloc[0]['SEARCH_ON'].replace(" ", "").lower()

            st.subheader(f"{fruit_chosen} Nutrition Information")

            try:
                response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
                if response.status_code == 200:
                    nutrition_df = pd.json_normalize(response.json())
                    st.dataframe(nutrition_df, use_container_width=True)
                elif response.status_code == 404:
                    st.warning(f"{fruit_chosen} not available in Fruityvice API (status: 404)")
                else:
                    st.warning(f"Could not fetch info for {fruit_chosen} (status: {response.status_code})")
            except Exception as e:
                st.error(f"Error fetching data for {fruit_chosen}: {e}")
        else:
            st.warning(f"'{fruit_chosen}' does not have a valid SEARCH_ON value in the database.")

    # Button to submit order
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
