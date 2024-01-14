import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from localizer import QuestLocalizer
from constants import MINECRAFT_LANGUAGES, MAX_FILES

if 'localize' not in st.session_state:
    st.session_state.localize = False

def localize_button():
    st.session_state.localize = True

def reset_localize_button():
    st.session_state.localize = False

def show_download_button(data: BytesIO, file_name: str):
    ste.download_button(
        label = f"Download {file_name}",
        data = data,
        file_name = file_name,
        mime = "application/octet-stream"
    )

st.set_page_config(
    page_title="FTB Quests Localization Tool",
    page_icon="📝",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/peunsu/ftbq-localization-tool",
        "Report a Bug": "https://github.com/peunsu/ftbq-localization-tool/issues",
        "About": '''
        ### FTB Quests Localization Tool\n
        InDev Version.\n
        Created by [peunsu](https://github.com/peunsu).\n
        [GitHub Repository](https://github.com/peunsu/ftbq-localization-tool)\n
        [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).\n
        '''
    }
)

st.title("FTB Quests Localization Tool")

st.subheader("Upload")

uploaded_files = st.file_uploader(
    label = "Upload your FTB Quest file(s) here.",
    type = ["snbt"],
    accept_multiple_files = True,
    help = "You can upload multiple files at once.",
    on_change = reset_localize_button
)

if not uploaded_files:
    st.stop()

if len(uploaded_files) > MAX_FILES:
    st.error(f"You can upload up to {MAX_FILES} files at once.")
    st.stop()

st.subheader("Language")
    
src = st.selectbox(
    label = "Select the source language.",
    options = MINECRAFT_LANGUAGES,
    index = None,
    format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})",
    on_change = reset_localize_button
)

dest = st.selectbox(
    label = "Select the destination language.",
    options = MINECRAFT_LANGUAGES,
    index = None,
    format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})",
    on_change = reset_localize_button
)

if not src or not dest:
    st.stop()

st.subheader("Localize!")

localizer = QuestLocalizer(uploaded_files, src, dest, "atm_9")

st.button(
    label = "Start localization",
    help = "Click this button to start localization.",
    on_click = localize_button,
    disabled = st.session_state.localize
)

if st.session_state.localize:
    st.toast(body="Localization started!", icon="📝")
    
    convert_bar_text = "Converting quests... ({progress})"
    convert_bar = st.progress(0, text=convert_bar_text)
    try:
        localizer.convert_quests(convert_bar, convert_bar_text)
    except Exception as e:
        st.error(f"An error occurred while converting quests: {e}")
        st.stop()
    
    translate_bar_text = "Translating quests... ({progress})"
    translate_bar = st.progress(0, text=translate_bar_text)
    try:
        localizer.translate_quests(translate_bar, translate_bar_text)
    except Exception as e:
        st.error(f"An error occurred while translating quests: {e}")
        st.stop()
    
    st.toast(body="Localization finished!", icon="📝")
    
    st.subheader("Result")
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_dir = localizer.compress_quests(tmp_dir)
        show_download_button(BytesIO(open(zip_dir, "rb").read()), "localized_snbt.zip")
    show_download_button(BytesIO(localizer.get_src_json().encode("utf-8")), f"{src}.json")
    show_download_button(BytesIO(localizer.get_dest_json().encode("utf-8")), f"{dest}.json")