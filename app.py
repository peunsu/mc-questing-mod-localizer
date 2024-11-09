import streamlit as st
from streamlit_extras.buy_me_a_coffee import button
from src import language_init, LanguageRadio

home_page = st.Page("home.py", title="Home", icon="🏠")
ftbq_page = st.Page("localizers/1_ftbq.py", title="FTB Quests", icon="👑")
ftbq_renewal_page = st.Page("localizers/2_ftbq_renewal.py", title="FTB Quests 1.21+ (Beta)", icon="⭐")
bqm_page = st.Page("localizers/3_bqm.py", title="Better Questing", icon="📖")

pg = st.navigation(
    {
        "Main": [home_page],
        "Localizers": [ftbq_page, ftbq_renewal_page, bqm_page]
    }
)

st.logo("static/logo.png", icon_image="static/icon.png")

st.set_page_config(
        page_title = "Minecraft Questing Mod Localizer",
        page_icon = "https://static.wikia.nocookie.net/minecraft_gamepedia/images/e/e9/Book_and_Quill_JE2_BE2.png",
        menu_items = {
            "Get help": "https://github.com/peunsu/mc-questing-mod-localizer",
            "Report a Bug": "https://github.com/peunsu/mc-questing-mod-localizer/issues",
            "About": '''
            ### Minecraft Questing Mod Localizer\n
            [![GitHub Release](https://img.shields.io/github/v/release/peunsu/mc-questing-mod-localizer?style=for-the-badge)](https://github.com/peunsu/mc-questing-mod-localizer/releases/latest)\n
            **[MIT License](https://github.com/peunsu/mc-questing-mod-localizer/blob/main/LICENSE) ⓒ 2024 [peunsu](https://github.com/peunsu)**\n
            ### Credits\n
            * **[FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb)**\n
            * **[Better Questing](https://www.curseforge.com/minecraft/mc-mods/better-questing) by [Funwayguy](https://www.curseforge.com/members/funwayguy)**\n
            ### Dependencies\n
            * [streamlit](https://github.com/streamlit/streamlit): A tool to build and share the web application with Python.
            * [googletrans](https://github.com/ssut/py-googletrans): Google translate API for Python.
            * [ftb-snbt-lib](https://github.com/peunsu/ftb-snbt-lib): Python library to parse, edit, and save FTB snbt tag.
            '''
        }
    )

language_init()
with st.sidebar:
    LanguageRadio().show()
    
button(username="peunsu")

pg.run()