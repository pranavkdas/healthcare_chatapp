import streamlit as st

__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

with st.sidebar:
    st.logo(
        image="https://cdn.prod.website-files.com/63cf306d39e6c9c427cad680/6579986076bdf4b7c6269536_mantys.svg",
        link="https://streamlit.io/gallery",
    )

home_page = st.Page("home.py", title="Home", icon=":material/home:")
second_page = st.Page(
    "second_page.py", title="Settings", icon=":material/settings_suggest:"
)

pg = st.navigation([home_page, second_page])
st.set_page_config(
    page_title="MantysIO",
    page_icon="https://cdn.prod.website-files.com/63cf306d39e6c9c427cad680/6579986076bdf4b7c6269536_mantys.svg",
)

pg.run()
