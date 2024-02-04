import streamlit as st

__all__ = [
    "localize_init",
    "language_init",
    "localize_button",
    "reset_localize_button",
    "set_page_config"
]

def localize_init() -> None:
    """Initialize the session state "localize" to False.
    """
    if 'localize' not in st.session_state:
        st.session_state.localize = False
        
def language_init() -> None:
    """Initialize the session state "lang" to "en_us".
    """
    if "lang" not in st.query_params:
        st.query_params.lang = "en_us"

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
            "Get help": "https://github.com/peunsu/mc-questing-mod-localizer",
            "Report a Bug": "https://github.com/peunsu/mc-questing-mod-localizer/issues",
            "About": '''
            ### Minecraft Questing Mod Localizer\n
            Minecraft Questing Mod Localizer is a web application that helps you to localize quest files of Minecraft questing mods.\n
            **[Release v{__version__}](https://github.com/peunsu/mc-questing-mod-localizer) ⓒ [peunsu](https://github.com/peunsu).**\n
            ### Credits\n
            * **[FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) ⓒ [FTB Team](https://www.curseforge.com/members/ftb).**\n
            * **[Better Questing](https://www.curseforge.com/minecraft/mc-mods/better-questing) ⓒ [Funwayguy](https://www.curseforge.com/members/funwayguy).**\n
            '''
        }
    )