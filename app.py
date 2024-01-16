import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from localizer import QuestLocalizer
from constants import MINECRAFT_LANGUAGES, MESSAGES, MAX_FILES, MAX_CHARS

if 'localize' not in st.session_state:
    st.session_state.localize = False

def localize_button() -> None:
    st.session_state.localize = True

def reset_localize_button() -> None:
    st.session_state.localize = False

def convert_quests_with_bar(localizer: QuestLocalizer) -> None:
    convert_bar_text = MESSAGES["convert_quests"]
    convert_bar = st.progress(0, text=convert_bar_text)
    try:
        localizer.convert_quests(convert_bar, convert_bar_text)
        convert_bar.progress(1.0, text=MESSAGES["convert_success"])
    except Exception as e:
        st.error(MESSAGES["convert_error"].format(e=e), icon="❌")
        st.stop()

def translate_quests_with_bar(localizer: QuestLocalizer) -> None:
    translate_bar_text = MESSAGES["translate_quests"]
    translate_bar = st.progress(0, text=translate_bar_text)
    try:
        localizer.translate_quests(translate_bar, translate_bar_text)
        translate_bar.progress(1.0, text=MESSAGES["translate_success"])
    except Exception as e:
        st.error(MESSAGES["translate_error"].format(e=e), icon="❌")
        st.stop()

def show_download_button(data: BytesIO, file_name: str) -> None:
    ste.download_button(
        label = MESSAGES["download_button"].format(file_name=file_name),
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
        Release v1.0.0 ([GitHub](https://github.com/peunsu/ftbq-localization-tool))\n
        Created by [peunsu](https://github.com/peunsu).\n
        [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).\n
        '''
    }
)

st.title("FTB Quests Localization Tool")

st.subheader("Upload")

uploaded_files = st.file_uploader(
    label = MESSAGES["uploader_label"],
    type = ["snbt"],
    accept_multiple_files = True,
    help = MESSAGES["uploader_help"],
    on_change = reset_localize_button,
)
if not uploaded_files:
    st.info(MESSAGES["uploader_empty"], icon="ℹ️")
    st.stop()
if len(uploaded_files) > MAX_FILES:
    st.error(MESSAGES["uploader_exceed"], icon="❌")
    st.stop()

st.subheader("Modpack")

modpack = st.text_input(
    label = MESSAGES["modpack_label"],
    value = "modpack",
    max_chars = MAX_CHARS,
    help = MESSAGES["modpack_help"],
    on_change = reset_localize_button
)

st.subheader("Language")

src = st.selectbox(
    label = MESSAGES["src_label"],
    options = MINECRAFT_LANGUAGES,
    index = list(MINECRAFT_LANGUAGES).index("en_us"),
    format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})",
    help = MESSAGES["src_help"],
    on_change = reset_localize_button
)
dest = st.selectbox(
    label = MESSAGES["dest_label"],
    options = MINECRAFT_LANGUAGES,
    index = list(MINECRAFT_LANGUAGES).index("en_us"),
    format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})",
    help = MESSAGES["dest_help"],
    on_change = reset_localize_button
)

st.subheader("Localize!")

localizer = QuestLocalizer(uploaded_files, src, dest, modpack)
st.button(
    label = MESSAGES["localize_label"],
    help = MESSAGES["localize_help"],
    on_click = localize_button,
    disabled = st.session_state.localize
)
if st.session_state.localize:
    st.toast(body=MESSAGES["localize_start"], icon="📝")
    convert_quests_with_bar(localizer)
    translate_quests_with_bar(localizer)
    st.toast(body=MESSAGES["localize_finish"], icon="📝")
    
    st.subheader("Result")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_dir = localizer.compress_quests(tmp_dir)
        show_download_button(BytesIO(open(zip_dir, "rb").read()), "localized_snbt.zip")
    show_download_button(BytesIO(localizer.get_src_json().encode("utf-8")), f"{src}.json")
    show_download_button(BytesIO(localizer.get_dest_json().encode("utf-8")), f"{dest}.json")

    with st.expander("Show JSON"):
        tab1, tab2 = st.tabs([f"{src}.json", f"{dest}.json"])
        tab1.json(localizer.get_src_json())
        tab2.json(localizer.get_dest_json())