import asyncio
import ftb_snbt_lib as slib

import streamlit as st

from src.constants import MINECRAFT_LANGUAGES, MINECRAFT_TO_GOOGLE, MINECRAFT_TO_DEEPL
from src.converter import SNBTConverter
from src.translator import GoogleTranslator, DeepLTranslator, GeminiTranslator
from src.utils import Message, read_file, check_deepl_key, check_gemini_key

Message("ftbq_new_title").title()
st.page_link(
    page = "pages/0_home.py",
    label = Message("back_to_home").text,
    icon = "↩️"
)

st.divider()

Message("ftbq_new_readme").info()

with st.container(border=True):
    Message("upload_lang_header").subheader()
    lang_file = st.file_uploader(
        label = Message("upload_lang_label_ftbq_new").text,
        type = ["snbt"],
        accept_multiple_files=False
    )

if not lang_file:
    st.stop()
    
with st.container(border=True):
    lang_list = list(MINECRAFT_LANGUAGES)
    
    Message("settings_header").subheader()
    
    translator_service = st.pills(
        label = Message("select_translator_label").text,
        options = ["Google", "DeepL", "Gemini"],
        default = "Google",
        key = "translator_service",
    )
    
    match translator_service:
        case "Google":
            lang_list = list(MINECRAFT_TO_GOOGLE)
            translator = GoogleTranslator()
        case "DeepL":
            deepl_key = st.session_state.deepl_key
            if not deepl_key:
                Message("api_key_empty", stop=True).info()
            if not check_deepl_key(deepl_key):
                Message("api_key_invalid", stop=True).error()
            lang_list = list(MINECRAFT_TO_DEEPL)
            translator = DeepLTranslator(auth_key=deepl_key)
        case "Gemini":
            gemini_key = st.session_state.gemini_key
            if not gemini_key:
                Message("api_key_empty", stop=True).info()
            if not check_gemini_key(gemini_key):
                Message("api_key_invalid", stop=True).error()
            translator = GeminiTranslator(auth_key=gemini_key)

    source_lang = st.selectbox(
        label = Message("select_source_lang_label").text,
        options = lang_list,
        index = lang_list.index("en_us"),
        format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
    )
    
    target_lang = st.selectbox(
        label = Message("select_target_lang_label").text,
        options = lang_list,
        index = lang_list.index("en_us"),
        format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
    )

    if source_lang == target_lang:
        Message("select_same_lang", stop=True).warning()

button = st.button(
    label = Message("start_button_label").text,
    type = "primary",
    use_container_width = True
)

if button:    
    status = st.status(
        label = Message("status_in_progress").text,
        expanded = True
    )

    try:
        Message("status_step_1", st_container=status).send()
        snbt_converter = SNBTConverter()
        source_lang_dict = snbt_converter.convert_snbt_to_json(slib.loads(read_file(lang_file)))
        target_lang_dict = {}
            
        Message("status_step_2", st_container=status).send()
        if source_lang_dict:
            asyncio.run(translator.translate(source_lang_dict, target_lang_dict, target_lang, status))
    except Exception as e:
        status.update(
            label = Message("status_error").text,
            state = "error"
        )
        status.error(f"An error occurred while localizing: {e}")
        st.stop()

    status.update(
        label = Message("status_done").text,
        state = "complete",
        expanded = False
    )
    
    with st.container(border=True):
        Message("downloads_header").subheader()
        
        source_lang_filename = f"{source_lang}.snbt"
        source_lang_download = st.download_button(
            label = source_lang_filename,
            data = slib.dumps(snbt_converter.convert_json_to_snbt(source_lang_dict)),
            file_name = source_lang_filename,
            on_click = "ignore",
            mime = "text/plain"
        )
        
        target_lang_filename = f"{target_lang}.snbt"
        target_lang_download = st.download_button(
            label = target_lang_filename,
            data = slib.dumps(snbt_converter.convert_json_to_snbt(target_lang_dict)),
            file_name = target_lang_filename,
            on_click = "ignore",
            mime = "text/plain"
        )

    with st.container(border=True):
        Message("user_guide_header").subheader()

        Message("user_guide_ftbq_new", source_lang=source_lang, target_lang=target_lang).send()