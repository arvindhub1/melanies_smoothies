import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

is_filled = st.checkbox("Mark this order as filled")

cnx = st.connection("snowflake")
session = cnx.session()

df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit in ingredients_list:
        row = df[df['FRUIT_NAME'] == fruit]
        st.subheader(f"{fruit} Nutrition Information")

        if row.empty or pd.isna(row.iloc[0]['SEARCH_ON']):
            st.warning(f"No nutrition info available for '{fruit}'.")
        else:
            search_on = row.iloc[0]['SEARCH_ON'].replace(" ", "").lower()
            try:
                resp = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
                if resp.status_code == 200:
                    nt_df = pd.json_normalize(resp.json())
                    st.dataframe(nt_df, use_container_width=True)
                elif resp.status_code == 404:
                    st.warning(f"{fruit} not supported by API (404).")
                else:
                    st.warning(f"Unexpected status for {fruit}: {resp.status_code}")
            except Exception as e:
                st.error(f"Error fetching {fruit}: {e}")

    if st.button('Submit Order'):
        try:
            stmt = f"""
              INSERT INTO smoothies.public.orders (ingredients, name_on_order, filled)
              VALUES ('{ingredients_string}', '{name_on_order}', {str(is_filled).upper()})
            """
            session.sql(stmt).collect()
            st.success(f"Order placed for {name_on_order}! ✅ Filled: {is_filled}")
        except Exception as e:
            st.error(f"Order submission failed: {e}")
