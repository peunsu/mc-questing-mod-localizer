import streamlit as st
from localizer import QuestLocalizer
from googletrans.constants import LANGUAGES

st.set_page_config(
    page_title="FTB Quests Localization Tool",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/peunsu/ftbq-localization-tool",
        "Report a Bug": "hhttps://github.com/peunsu/ftbq-localization-tool/issues",
        "About": '''
        ### FTB Quests Localization Tool\n
            InDev Version.\n
            GitHub: https://github.com/peunsu/ftbq-localization-tool
        '''
    }
)

st.title("FTB Quests Localization Tool")

uploaded_files = st.file_uploader(
    label = "Upload your FTB Quest file(.snbt) here.",
    type = ["snbt"],
    accept_multiple_files = True,
    help = "You can upload multiple files at once."
)
    
src = st.selectbox(
    label = "Select the source language.",
    options = ["English", "Korean"]
)

dest = st.selectbox(
    label = "Select the destination language.",
    options = ["English", "Korean"]
)

localizer = QuestLocalizer(uploaded_files, "en_us", "ko_kr", "atm9")
localizer.convert_quests()
st.json(localizer.src_lang.json)
