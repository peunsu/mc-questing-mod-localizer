import streamlit as st

def localize_init() -> None:
    if 'localize' not in st.session_state:
        st.session_state.localize = False
        
def language_init() -> None:
    if "lang" not in st.query_params:
        st.query_params.lang = "en_us"

def localize_button() -> None:
    st.session_state.localize = True

def reset_localize_button(*args) -> None:
    st.session_state.localize = False

def set_page_config(title: str, icon: str) -> None:
    st.set_page_config(
        page_title = title,
        page_icon = icon,
        menu_items = {
            "Get help": "https://github.com/peunsu/mc-questing-mod-localizer",
            "Report a Bug": "https://github.com/peunsu/mc-questing-mod-localizer/issues",
            "About": '''
            ### Minecraft Questing Mod Localizer\n
            [Minecraft Questing Mod Localizer](https://github.com/peunsu/mc-questing-mod-localizer) is a web application that helps you to localize quest files of Minecraft questing mods.\n
            [![GitHub Release](https://img.shields.io/github/v/release/peunsu/mc-questing-mod-localizer?style=for-the-badge)](https://github.com/peunsu/mc-questing-mod-localizer/releases/latest)\n
            **ⓒ [peunsu](https://github.com/peunsu)**.\n
            ### Credits\n
            * **[FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).**\n
            * **[Better Questing](https://www.curseforge.com/minecraft/mc-mods/better-questing) by [Funwayguy](https://www.curseforge.com/members/funwayguy).**\n
            '''
        }
    )