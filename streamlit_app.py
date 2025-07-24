# Import Python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
# Set the app title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input field
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")
cnx=st.connection("snowflake")
session =cnx.session()
# Get current Snowflake session
#session = get_active_session()

# Get fruit options
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Multiselect for ingredients (limit to 5)
ingredients_selected = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

if ingredients_list:
    ingredients_string=''

    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+''
        st.subheader(fruit_chosen+'Nutrition Information')
        smoothiefroot_response=requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

# Submit Order
if st.button("Submit Order"):
    if not name_on_order:
        st.warning("Please enter a name for your Smoothie!")
    elif not ingredients_selected:
        st.warning("Please select at least one ingredient!")
    else:
        ingredients_str = " ".join(ingredients_selected)
        # Create insert statement
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_str}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")



smoothiefroot_response = requests.get("https://my.fruityvice.com/api/fruit/watermelon")
sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

