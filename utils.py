import streamlit as st
from constants import VERSION

def localize_init() -> None:
    """Initialize the session state "localize" to False.
    """
    if 'localize' not in st.session_state:
        st.session_state.localize = False

def localize_button() -> None:
    """Set the session state "localize" to True.
    """
    st.session_state.localize = True

def reset_localize_button() -> None:
    """Set the session state "localize" to False.
    """
    st.session_state.localize = False
    
def set_page_config(title: str, icon: str) -> None:
    st.set_page_config(
        page_title = title,
        page_icon = icon,
        menu_items = {
            "Get help": "https://github.com/peunsu/ftbq-localization-tool",
            "Report a Bug": "https://github.com/peunsu/ftbq-localization-tool/issues",
            "About": '''
            ### Minecraft Quest Mod Localizer\n
            Release v{VERSION} ([GitHub](https://github.com/peunsu/ftbq-localization-tool))\n
            Created by [peunsu](https://github.com/peunsu).\n
            [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).\n
            '''.format(VERSION=VERSION)
        }
    )