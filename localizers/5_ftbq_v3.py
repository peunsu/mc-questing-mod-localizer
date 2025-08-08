import json
import deepl
import asyncio
import streamlit as st
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from stqdm import stqdm
from src.components import *
from src.constants import *
from src.converter import FTBQuestConverter
from src.translator import GoogleTranslator, DeepLTranslator
from src.utils import read_file, write_file

with st.sidebar:
    deepl_key = st.text_input(
        label = Message("deepl_key_label").text,
        type = "password",
        key = "deepl_key",
    )
    st.caption(Message("deepl_key_caption").text)

Message("ftbq_title").title()
st.page_link(
    page = "home.py",
    label = Message("back_to_home").text,
    icon = "↩️"
)

st.divider()

st.info("""
    ### Read Me
    - Quest files (`.snbt`) are in the `config/ftbquests/quests` folder of the modpack.
    - Language files (`.json`) are in the `kubejs/assets/kubejs/lang` folder of the modpack. The directory may vary depending on the modpack.
""")

with st.form("task_form"):    
    Message("header_modpack_name").subheader()
    modpack_name = st.text_input(
        label = Message("modpack_label").text,
        max_chars = 16,
        placeholder = "atm9",
    )
    
    Message("header_select_task").subheader()
    task = st.radio(
        label = Message("select_task_label").text,
        options = [0, 1, 2],
        format_func = lambda x: {
            0: Message("select_task_convert").text,
            1: Message("select_task_convert_no_translate").text,
            2: Message("select_task_translate_only").text,
        }[x],
        key = "task"
    )
    
    with st.expander(Message("expander_select_task_label").text):
        Message("expander_select_task").send()
    
    Message("header_lang_check").subheader()
    lang_exists = st.radio(
        label = "Do you have a language file in the modpack? Check a language file in the `kubejs/assets/kubejs/lang` folder of the modpack. The directory may vary depending on the modpack.",
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
    st.error("Nothing to do with your selected task. Please select other task.")
    st.stop()

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
        Message("header_upload_quest").subheader()
        quest_files = st.file_uploader(
            label = "Upload all quest files (`.snbt`) in the `config/ftbquests/quests` folder of the modpack.",
            type = ["snbt"],
            accept_multiple_files=True
        )

    if st.session_state.lang_exists:
        Message("header_upload_lang").subheader()
        lang_file = st.file_uploader(
            label = "Upload a language file (`.json`) in the `kubejs/assets/kubejs/lang` folder of the modpack. The directory may vary depending on the modpack.",
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
        st.subheader("Translator Options")
        
        translator_service = st.pills(
            label = "Select a translator service.",
            options = ["Google", "DeepL"],
            default = "Google",
            key = "translator_service",
        )
        
        if translator_service == "Google":
            lang_list = list(MINECRAFT_TO_GOOGLE)
            translator = GoogleTranslator()
        elif translator_service == "DeepL":
            if deepl_key:
                try:
                    with st.spinner("Checking your API key..."):
                        deepl_client = deepl.DeepLClient(deepl_key)
                        usage = deepl_client.get_usage()
                    st.progress(usage.character.count / usage.character.limit, text=f"Your API key's current usage: {usage.character.count}/{usage.character.limit} characters")
                    if usage.character.count >= usage.character.limit:
                        st.error("Your API key has reached its limit. Please use another API key.")
                        st.stop()
                except:
                    st.error("The API key is invalid. Please enter a valid API key.")
                    st.stop()
            else:
                st.info("Please enter your API key in the sidebar to proceed.")
                st.stop()
            lang_list = list(MINECRAFT_TO_DEEPL)
            translator = DeepLTranslator(auth_key=deepl_key)

with st.container(border=True):
    st.subheader("Language Options")
    source_lang = st.selectbox(
        label = Message("src_label").text,
        options = lang_list,
        index = lang_list.index("en_us"),
        format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
    )
    
    if st.session_state.do_translate:
        target_lang = st.selectbox(
            label = Message("dest_label").text,
            options = lang_list,
            index = lang_list.index("en_us"),
            format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
        )
    
        if source_lang == target_lang:
            Message("translate_same_lang").warning()
            st.stop()

button = st.button("Start", type="primary", use_container_width=True)

if button:
    status = st.status("Localizing quests...", expanded=True)
    
    source_lang_dict = json.loads(read_file(lang_file)) if st.session_state.lang_exists else {}
    target_lang_dict = {}
    
    if st.session_state.do_convert:
        status.write("**Step 1.** Converting quests...")
        converter = FTBQuestConverter(modpack_name, quest_files)
        converter.lang_dict.update(source_lang_dict)
        converted_quest_arr, source_lang_dict = converter.convert()
        
    if st.session_state.do_translate:
        status.write("**Step 2.** Translating quests... (It may take a long time - **Do not exit the page!**)")
        if source_lang_dict:
            asyncio.run(translator.translate(source_lang_dict, target_lang_dict, target_lang, status))

    status.success("Done!", icon="✅")

    st.subheader("Downloads")
    
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