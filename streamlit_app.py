# Import necessary packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col
from snowflake.snowpark import Row

# Title of the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Let user select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Only proceed if user selects ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # use comma-separated list

    # Show nutrition info for each fruit
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            if response.ok:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"Could not fetch info for {fruit_chosen}")
        except:
            st.error(f"API call failed for {fruit_chosen}")

    # Button to insert order
    if st.button('Submit order'):
        try:
            # Prevent inserting if name is empty
            if not name_on_order.strip():
                st.warning("Please enter a name for the smoothie.")
            else:
                # Insert using safe method
                new_order_df = session.create_dataframe(
                    [Row(INGREDIENTS=ingredients_string, NAME_ON_ORDER=name_on_order)],
                    schema=["INGREDIENTS", "NAME_ON_ORDER"]
                )
                new_order_df.write.save_as_table("smoothies.public.orders", mode="append")
                st.success('✅ Your Smoothie is ordered!')
        except Exception as e:
            st.error(f"❌ Failed to insert order: {e}")
