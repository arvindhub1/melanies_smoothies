# Import Python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Streamlit app title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect input for fruit choices
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If fruits are selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # comma-separated string like DORA expects

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Call the Fruityvice API
        fruityvice_url = f"https://fruityvice.com/api/fruit/{search_on}"
        response = requests.get(fruityvice_url)

        if response.status_code == 200:
           st.subheader(f"{fruit_chosen} Nutrition Information")
           st.dataframe(data=response.json(), use_container_width=True)
        else:
           st.subheader(f"{fruit_chosen} Nutrition Information")
           st.info(f"Nutrition info not found in Fruityvice. This fruit may not be available in the API (e.g., Ximenia).")


    # Build SQL statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit order button
    if st.button('Submit order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Order failed to submit: {e}")
