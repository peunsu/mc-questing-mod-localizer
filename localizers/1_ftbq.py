import json
import asyncio
import streamlit as st
from tempfile import TemporaryDirectory
from src.components import *
from src.constants import *
from src.converter import FTBQuestConverter
from src.translator import GoogleTranslator, DeepLTranslator, GeminiTranslator
from src.utils import read_file, check_deepl_key, check_gemini_key

with st.sidebar:
    deepl_key = st.text_input(
        label = Message("deepl_key_label").text,
        type = "password",
        key = "deepl_key",
        help = Message("deepl_key_help").text
    )
    gemini_key = st.text_input(
        label = "Gemini API Key",
        type = "password",
        key = "gemini_key",
        help = Message("gemini_key_help").text
    )
    Message("api_key_caption").caption()

Message("ftbq_title").title()
st.page_link(
    page = "home.py",
    label = Message("back_to_home").text,
    icon = "↩️"
)

st.divider()

Message("ftbq_readme").info()

with st.form("task_form"):
    Message("modpack_name_header").subheader()
    modpack_name = st.text_input(
        label = Message("modpack_name_label").text,
        max_chars = 16,
        placeholder = "atm9",
    )
    
    Message("select_task_header").subheader()
    task = st.radio(
        label = Message("select_task_label").text,
        options = [0, 1, 2],
        format_func = lambda x: {
            0: Message("select_task_convert_translate").text,
            1: Message("select_task_convert_no_translate").text,
            2: Message("select_task_translate_only").text,
        }[x],
        key = "task"
    )
    
    with st.expander(Message("select_task_expander_label").text):
        Message("select_task_expander_desc").send()
    
    Message("lang_check_header").subheader()
    lang_exists = st.radio(
        label = Message("lang_check_label").text,
        options = [True, False],
        format_func = lambda x: {
            True: "Yes",
            False: "No",
        }[x],
        key = "lang_exists",
    )
    
    task_submit = st.form_submit_button()

    if not task_submit and not st.session_state.get("task_submit"):
        st.stop()
        
    st.session_state.task_submit = True

if task == 2 and not lang_exists:
    Message("select_task_nothing", stop=True).error()

match task:
    case 0:
        st.session_state.do_convert = True
        st.session_state.do_translate = True
    case 1:
        st.session_state.do_convert = True
        st.session_state.do_translate = False
    case 2:
        st.session_state.do_convert = False
        st.session_state.do_translate = True

with st.container(border=True):    
    if st.session_state.do_convert:
        Message("upload_quest_header").subheader()
        quest_files = st.file_uploader(
            label = Message("upload_quest_label_ftbq").text,
            type = ["snbt"],
            accept_multiple_files=True
        )

    if st.session_state.lang_exists:
        Message("upload_lang_header").subheader()
        lang_file = st.file_uploader(
            label = Message("upload_lang_label_ftbq").text,
            type = ["json"],
            accept_multiple_files=False
        )

if st.session_state.do_convert and not quest_files:
    st.stop()
if st.session_state.lang_exists and not lang_file:
    st.stop()
    
with st.container(border=True):
    lang_list = list(MINECRAFT_LANGUAGES)
    if st.session_state.do_translate:
        st.subheader("Settings")
        
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
                if not deepl_key:
                    Message("api_key_empty", stop=True).info()
                if not check_deepl_key(deepl_key):
                    Message("api_key_invalid", stop=True).error()
                lang_list = list(MINECRAFT_TO_DEEPL)
                translator = DeepLTranslator(auth_key=deepl_key)
            case "Gemini":
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
    
    if st.session_state.do_translate:
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

    source_lang_dict = json.loads(read_file(lang_file)) if st.session_state.lang_exists else {}
    target_lang_dict = {}
    
    if st.session_state.do_convert:
        Message("status_step_1", st_container=status).send()
        converter = FTBQuestConverter(modpack_name, quest_files)
        converter.lang_dict.update(source_lang_dict)
        converted_quest_arr, source_lang_dict = converter.convert()
        
    if st.session_state.do_translate:
        Message("status_step_2", st_container=status).send()
        if source_lang_dict:
            asyncio.run(translator.translate(source_lang_dict, target_lang_dict, target_lang, status))

    status.update(
        label = Message("status_done").text,
        state = "complete",
        expanded = False
    )
    
    with st.container(border=True):
        Message("downloads_header").subheader()
        
        if st.session_state.do_convert:
            with TemporaryDirectory() as temp_dir:
                zip_filename = "quests.zip"
                zip_dir = converter.compress(temp_dir, zip_filename)
                
                quest_zip_download = st.download_button(
                    label = zip_filename,
                    data = open(zip_dir, "rb"),
                    file_name = zip_filename,
                    on_click = "ignore",
                    mime = "application/zip"
                )
            
            source_lang_filename = f"{source_lang}.json"
            source_lang_download = st.download_button(
                label = source_lang_filename,
                data = json.dumps(converter.lang_dict, indent=4, ensure_ascii=False),
                file_name = source_lang_filename,
                on_click = "ignore",
                mime = "application/json"
            )
        
        if st.session_state.do_translate:
            target_lang_filename = f"{target_lang}.json"
            target_lang_download = st.download_button(
                label = target_lang_filename,
                data = json.dumps(target_lang_dict, indent=4, ensure_ascii=False),
                file_name = target_lang_filename,
                on_click = "ignore",
                mime = "application/json"
            )

    with st.container(border=True):
        Message("user_guide_header").subheader()

        Message("user_guide_ftbq_1").send()
        if st.session_state.do_translate:
            Message("user_guide_ftbq_2", source_lang=source_lang, target_lang=target_lang).send()
        else:
            Message("user_guide_ftbq_3", source_lang=source_lang).send()