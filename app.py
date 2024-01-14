import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from localizer import QuestLocalizer
from constants import MINECRAFT_LANGUAGES

if 'localize' not in st.session_state:
    st.session_state.localize = False

def localize_button():
    st.session_state.localize = True

st.set_page_config(
    page_title="FTB Quests Localization Tool",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/peunsu/ftbq-localization-tool",
        "Report a Bug": "hhttps://github.com/peunsu/ftbq-localization-tool/issues",
        "About": '''
        ### FTB Quests Localization Tool\n
            InDev Version.\n
            GitHub: https://github.com/peunsu/ftbq-localization-tool
        '''
    }
)

st.title("FTB Quests Localization Tool")

uploaded_files = st.file_uploader(
    label = "Upload your FTB Quest file(s) here.",
    type = ["snbt"],
    accept_multiple_files = True,
    help = "You can upload multiple files at once."
)
    
src = st.selectbox(
    label = "Select the source language.",
    options = MINECRAFT_LANGUAGES,
    format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
)

dest = st.selectbox(
    label = "Select the destination language.",
    options = MINECRAFT_LANGUAGES,
    format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
)

localizer = QuestLocalizer(uploaded_files, src, dest, "atm_9")

st.button(
    label = "Start localization",
    help = "Click this button to start localization.",
    on_click = localize_button
)

if st.session_state.localize:
    localizer.convert_quests()
    localizer.translate_quests()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_dir = localizer.compress_quests(tmp_dir)
        ste.download_button(
            label = f"Download quests.zip",
            data = BytesIO(open(zip_dir, "rb").read()),
            file_name = "quests.zip",
            mime = "application/octet-stream"
        )
        
    ste.download_button(
        label = f"Download {src}.json",
        data = BytesIO(localizer.get_src_json().encode("utf-8")),
        file_name = f"{src}.json",
        mime = "application/octet-stream"
    )
    ste.download_button(
        label = f"Download {dest}.json",
        data = BytesIO(localizer.get_dest_json().encode("utf-8")),
        file_name = f"{dest}.json",
        mime = "application/octet-stream"
    )