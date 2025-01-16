import streamlit as st


with st.sidebar:
    st.logo(
        image="https://cdn.prod.website-files.com/63cf306d39e6c9c427cad680/6579986076bdf4b7c6269536_mantys.svg",
        link="https://streamlit.io/gallery",
    )
    # openai_api_key = st.text_input(
    #     "OpenAI API Key", key="chatbot_api_key", type="password"
    # )

home_page = st.Page("home.py", title="Home", icon=":material/house:")
second_page = st.Page(
    "second_page.py", title="Second page", icon=":material/add_circle:"
)

pg = st.navigation([home_page, second_page])
st.set_page_config(
    page_title="MantysIO",
    page_icon="https://cdn.prod.website-files.com/63cf306d39e6c9c427cad680/6579986076bdf4b7c6269536_mantys.svg",
)

pg.run()
