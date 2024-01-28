import streamlit as st
from utils import set_page_config
from components import Message

set_page_config(
    title = "Minecraft Quest Mod Localizer",
    icon = "https://media.forgecdn.net/avatars/275/363/637261948352026071.png"
)

st.title("Minecraft Quest Mod Localizer")
st.caption(Message("version").text)