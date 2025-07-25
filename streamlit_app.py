# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get active Snowflake session
cnx=st.connection("snowflake")
session = cnx.session()

# Fetch available fruit options from the database
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_df]

# Let user choose fruits (up to 5)
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_list, max_selections=5)

# Only allow submission when name and ingredients are filled
if name_on_order and ingredients_list:
    # Convert list to a comma-separated string with single quotes
    ingredients_string = ', '.join(ingredients_list)

    if st.button("Submit Order"):
        # Create SQL insert statement
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        # Execute the insert
        session.sql(insert_stmt).collect()

        # Confirmation message
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
# 🥤 Call the SmoothieFroot API
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# Check the raw response (status code)
#st.text(smoothiefroot_response.json())
sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
