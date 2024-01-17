import tempfile
import streamlit as st
import streamlit_ext as ste
import streamlit.components.v1 as components

from io import BytesIO
from localizer import QuestLocalizer
from constants import MINECRAFT_LANGUAGES, MINECRAFT_LOCALES, MESSAGES, MAX_FILES, MAX_CHARS

if 'localize' not in st.session_state:
    st.session_state.localize = False

def localize_button() -> None:
    st.session_state.localize = True

def reset_localize_button() -> None:
    st.session_state.localize = False
    
def lang_index(lang: str) -> int:
    return list(MINECRAFT_LANGUAGES).index(lang)

def lang_format(lang: str) -> str:
    return f"{lang} ({MINECRAFT_LANGUAGES[lang]})"

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

def snbt_download_button(localizer: QuestLocalizer) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_dir = localizer.compress_quests(tmp_dir)
        show_download_button(BytesIO(open(zip_dir, "rb").read()), "localized_snbt.zip")

def json_download_button(localizer: QuestLocalizer, template: bool = False) -> None:
    if template:
        show_download_button(BytesIO(localizer.get_template_json().encode("utf-8")), "template_lang.json")
        with st.expander("Show JSON"):
            st.json(localizer.get_template_json())
        return
    
    if st.session_state.translate:
        show_download_button(BytesIO(localizer.get_src_json().encode("utf-8")), f"{src}.json")
        show_download_button(BytesIO(localizer.get_dest_json().encode("utf-8")), f"{dest}.json")
        with st.expander("Show JSON"):
            tab1, tab2 = st.tabs([f"{src}.json", f"{dest}.json"])
            tab1.json(localizer.get_src_json())
            tab2.json(localizer.get_dest_json())
    else:
        show_download_button(BytesIO(localizer.get_src_json().encode("utf-8")), f"{src}.json")
        with st.expander("Show JSON"):
            st.json(localizer.get_src_json())

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

st.subheader("Upload FTB Quests Files")

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

st.subheader("Modpack Name")

modpack = st.text_input(
    label = MESSAGES["modpack_label"],
    value = "modpack",
    max_chars = MAX_CHARS,
    help = MESSAGES["modpack_help"],
    on_change = reset_localize_button
)

st.subheader("Auto Translate")

st.radio(
    label = "Do you want to translate the quests automatically using Google Translate?",
    options = [True, False],
    format_func = lambda x: "Yes" if x else "No",
    index = 1,
    help = "If you select 'Yes', the quests will be translated automatically using Google Translate.",
    on_change = reset_localize_button,
    key = "translate"
)

src = st.selectbox(
    label = MESSAGES["src_label"],
    options = MINECRAFT_LANGUAGES,
    index = lang_index("en_us"),
    format_func = lang_format,
    help = MESSAGES["src_help"],
    on_change = reset_localize_button
)

dest = st.selectbox(
    label = MESSAGES["dest_label"],
    options = MINECRAFT_LANGUAGES,
    index = lang_index("en_us") if st.session_state.translate else lang_index(src),
    format_func = lang_format,
    help = MESSAGES["dest_help"],
    on_change = reset_localize_button,
    disabled = not st.session_state.translate
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
    if st.session_state.translate:
        translate_quests_with_bar(localizer)
    
    st.toast(body=MESSAGES["localize_finish"], icon="📝")
    
    st.subheader("How to Apply Localization")
    
    st.write("1. Download `localized_snbt.zip`. (Click the button below)")
    snbt_download_button(localizer)
    # with tempfile.TemporaryDirectory() as tmp_dir:
    #     zip_dir = localizer.compress_quests(tmp_dir)
    #     show_download_button(BytesIO(open(zip_dir, "rb").read()), "localized_snbt.zip")
        
    st.write("2. Extract `localized_snbt.zip` and replace the original `.snbt` files in `config/ftbquests/quests` folder with the extracted files.")
    
    if st.session_state.translate:
        st.write(f"3. Download `{src}.json` and `{dest}.json`. (Click the buttons below)")
        json_download_button(localizer)
        st.write(f"4. Put `{src}.json` and `{dest}.json` in `kubejs/assets/kubejs/lang` folder.")
        st.write(f"5. Done! If you want to fix mistranslated text, edit `{dest}.json`.")
        st.warning(f"Do not change `{src}.json`.", icon="⚠️")
    else:
        st.write(f"3. Download `{src}.json`. (Click the button below)")
        json_download_button(localizer)
        st.write(f"4. Put `{src}.json` in `kubejs/assets/kubejs/lang` folder.")
        st.write(f"5. Done!")
    
    st.subheader("How to Add New Language Manually")
    
    st.write("1. Download `template_lang.json`. (Click the button below)")
    json_download_button(localizer, template=True)
    
    st.write("2. Rename `template_lang.json` to `<language>.json`. [Example: `en_us.json`]")
    st.link_button(
        label = "List of Minecraft Languages",
        url = "https://minecraft.fandom.com/wiki/Language#Languages",
        help = "Click this link to see the list of Minecraft languages."
    )
    
    st.write(f"3. Translate the text in `{src}.json` and put the translated text in `<language>.json`. You can use this localization tool or any translator to translate the text.")
    st.warning(f"Do not change `{src}.json`. The translated text should be put in `<language>.json`.", icon="⚠️")
    st.write("4. Put `<language>.json` in `kubejs/assets/kubejs/lang` folder.")
    st.write("5. Done!")