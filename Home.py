import streamlit as st
from utils import set_page_config
from components import Message

set_page_config(
    title = "Minecraft Questing Mod Localizer",
    icon = "https://static.wikia.nocookie.net/minecraft_gamepedia/images/e/e9/Book_and_Quill_JE2_BE2.png"
)

st.title("Minecraft Questing Mod Localizer")
st.caption(Message("version").text)

st.page_link("pages/1_FTB_Quests.py", label="FTB Quests", icon="👑")
st.page_link("pages/2_Better_Questing.py", label="Better Questing", icon="📖")