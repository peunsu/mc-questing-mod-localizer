import streamlit as st
from src import language_init, set_page_config

language_init()

set_page_config(
    title = "Minecraft Questing Mod Localizer",
    icon = "https://static.wikia.nocookie.net/minecraft_gamepedia/images/e/e9/Book_and_Quill_JE2_BE2.png"
)

st.title("Minecraft Questing Mod Localizer")

st.page_link("pages/1_👑_FTB_Quests.py", label="FTB Quests", icon="👑")
st.page_link("pages/2_📖_Better_Questing.py", label="Better Questing", icon="📖")

st.divider()

st.subheader("About")
st.write("Minecraft Questing Mod Localizer is a web application that helps you to localize quest files of Minecraft questing mods.\
        You can convert quest files to localizable format, translate quest files to other languages, and apply the translated quest files to the modpack.\
        This application supports FTB Quests and Better Questing.")
st.write("마인크래프트 퀘스트 모드 로컬라이저는 마인크래프트 퀘스트 모드의 퀘스트 파일을 쉽게 로컬라이징해주는 웹 어플리케이션입니다.\
        퀘스트 파일을 로컬라이징 가능한 포맷으로 변환하고, 다른 언어로 번역하고, 번역한 텍스트를 모드팩에 적용할 수 있습니다.\
        FTB Quests와 Better Questing을 지원합니다.")

st.subheader("Contact")
st.write("* [GitHub Repository](https://github.com/peunsu/mc-questing-mod-localizer)")
st.write("* [Discord Server (Mystic Red Space)](https://discord.gg/Z8j6ahF4MJ)")
st.write("* [Email](mailto:peunsu55@gmail.com)")

st.subheader("License")
st.write("[MIT License](https://github.com/peunsu/mc-questing-mod-localizer/blob/main/LICENSE) © 2024 peunsu")
