import logging
import streamlit as st
from streamlit_extras.buy_me_a_coffee import button

from src.utils import get_session_id

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger("httpx").setLevel(logging.WARNING)  # Suppress httpx logs

logger = logging.getLogger(f"{__name__} ({get_session_id()})")

logger.info("Connection established")

home_page = st.Page("pages/0_home.py", title="Home", icon="🏠")
ftbq_page = st.Page("pages/1_ftbq.py", title="FTB Quests Localizer", icon="👑")
ftbq_new_page = st.Page("pages/2_ftbq_new.py", title="FTB Quests Localizer (1.21+)", icon="⭐")
bqm_page = st.Page("pages/3_bqm.py", title="Better Questing Localizer", icon="📖")

pg = st.navigation(
    {
        "Main": [home_page],
        "FTB Quests": [ftbq_page, ftbq_new_page],
        "Better Questing": [bqm_page],
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
            **[MIT License](https://github.com/peunsu/mc-questing-mod-localizer/blob/main/LICENSE) ⓒ 2024-2025 [peunsu](https://github.com/peunsu)**\n
            ### Credits\n
            * **[FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb)**\n
            * **[Better Questing](https://www.curseforge.com/minecraft/mc-mods/better-questing) by [Funwayguy](https://www.curseforge.com/members/funwayguy)**\n
            ### Dependencies\n
            * [streamlit](https://github.com/streamlit/streamlit): A tool to build and share the web application with Python.
            * [googletrans](https://github.com/ssut/py-googletrans): Google translate API for Python.
            * [deepl-python](https://github.com/DeepLcom/deepl-python): DeepL API client for Python.
            * [langchain](https://github.com/langchain-ai/langchain): A framework for developing applications powered by language models.
            * [ftb-snbt-lib](https://github.com/peunsu/ftb-snbt-lib): Python library to parse, edit, and save FTB snbt tag.
            '''
        }
    )

if st.context.locale in ("ko-KR", "ko"):
    st.session_state.language = "ko-KR"
else:
    st.session_state.language = "en-US"

with st.sidebar:
    language_selector = st.pills(
        "Site Language",
        options=["en-US", "ko-KR"],
        selection_mode="single",
        default=st.session_state.language,
        format_func=lambda x: {
            "en-US": "English",
            "ko-KR": "한국어",
        }[x]
    )
    st.session_state.language = language_selector
    
button(username="peunsu")

pg.run()