from __future__ import annotations

import streamlit as st

from localizer import QuestLocalizer
from utils import Message, Manager, lang_index, lang_format
from constants import MINECRAFT_LANGUAGES, MAX_FILES, MAX_CHARS

VERSION = "1.2.0"

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

st.set_page_config(
    page_title="FTB Quests Localization Tool",
    page_icon="https://media.forgecdn.net/avatars/275/363/637261948352026071.png",
    menu_items={
        "Get help": "https://github.com/peunsu/ftbq-localization-tool",
        "Report a Bug": "https://github.com/peunsu/ftbq-localization-tool/issues",
        "About": '''
        ### FTB Quests Localization Tool\n
        Release v{VERSION} ([GitHub](https://github.com/peunsu/ftbq-localization-tool))\n
        Created by [peunsu](https://github.com/peunsu).\n
        [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).\n
        '''.format(VERSION=VERSION)
    }
)

st.title("FTB Quests Localization Tool")
st.caption("Version {VERSION}".format(VERSION=VERSION))

st.subheader("Upload FTB Quests Files")

uploaded_files = st.file_uploader(
    label = Message("uploader_label").text,
    type = ["snbt"],
    accept_multiple_files = True,
    help = Message("uploader_help").text,
    on_change = reset_localize_button,
)
if not uploaded_files:
    Message("uploader_empty", stop=True).info()
if len(uploaded_files) > MAX_FILES:
    Message("uploader_exceed", stop=True).error()

st.subheader("Modpack Name")

modpack = st.text_input(
    label = Message("modpack_label").text,
    value = "modpack",
    max_chars = MAX_CHARS,
    help = Message("modpack_help").text,
    on_change = reset_localize_button
)

st.subheader("Auto Translate")

st.radio(
    label = Message("auto_translate_label").text,
    options = [True, False],
    format_func = lambda x: "Yes" if x else "No",
    index = 1,
    help = Message("auto_translate_help").text,
    on_change = reset_localize_button,
    key = "translate"
)

src = st.selectbox(
    label = Message("src_label").text,
    options = MINECRAFT_LANGUAGES,
    index = lang_index("en_us"),
    format_func = lang_format,
    help = Message("src_help").text,
    on_change = reset_localize_button
)

dest = st.selectbox(
    label = Message("dest_label").text,
    options = MINECRAFT_LANGUAGES,
    index = lang_index("en_us"),
    format_func = lang_format,
    help = Message("dest_help").text,
    on_change = reset_localize_button,
    disabled = not st.session_state.translate
)

st.subheader("Localize!")

localizer = QuestLocalizer(uploaded_files, src, dest, modpack)

st.button(
    label = Message("localize_label").text,
    help = Message("localize_help").text,
    on_click = localize_button,
    disabled = st.session_state.localize
)

if st.session_state.localize:
    manager = Manager(localizer)
    manager.run()
    
    st.subheader("How to Apply Localization")
    
    Message("apply_manual_1").send()
    manager.download_snbt()
    Message("apply_manual_2").send()
    if st.session_state.translate:
        Message("apply_manual_3_1", src=src, dest=dest).send()
        manager.download_json()
        Message("apply_manual_4_1", src=src, dest=dest).send()
        Message("apply_manual_5_1", dest=dest).send()
    else:
        Message("apply_manual_3_2", src=src).send()
        manager.download_json()
        Message("apply_manual_4_2", src=src).send()
        Message("apply_manual_5_2").send()
    Message("apply_manual_warning", src=src).warning()
    
    st.subheader("How to Add New Language Manually")
    
    Message("add_manual_1").send()
    manager.download_json(template=True)
    Message("add_manual_2").send()
    st.link_button(
        label = Message("lang_link_label").text,
        url = Message("lang_link_url").text,
        help = Message("lang_link_help").text
    )
    Message("add_manual_3", src=src).send()
    Message("add_manual_warning", src=src).warning()
    Message("add_manual_4").send()
    Message("add_manual_5").send()