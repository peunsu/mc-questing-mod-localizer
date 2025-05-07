import deepl
import streamlit as st
from src.components import *
from src.constants import *

Message("ftbq_title").title()
st.page_link(
    page = "home.py",
    label = Message("back_to_home").text,
    icon = "↩️"
)

st.divider()

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
with st.expander(Message("expander_check_label").text):
    Message("expander_check_ftbq").send()

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

if st.session_state.do_convert:
    Message("header_upload_quest").subheader()
    quest_files = st.file_uploader(
        label = "Upload all quest files (`.snbt`) in the `config/ftbquests/quests` folder of the modpack.",
        type = ["snbt"],
        accept_multiple_files=True
    )

Message("header_lang_check").subheader()
lang_exists = st.radio(
    label = "Do you have a language file in the modpack? Check a language file in the `kubejs/assets/kubejs/lang` folder of the modpack. The directory may vary depending on the modpack.",
    options = [True, False],
    format_func = lambda x: {
        True: "Yes",
        False: "No",
    }[x],
    index = 1,
    key = "lang_exists",
)

if st.session_state.lang_exists:
    Message("header_upload_lang").subheader()
    lang_files = st.file_uploader(
        label = "Upload a language file (`.json`) in the `kubejs/assets/kubejs/lang` folder of the modpack. The directory may vary depending on the modpack.",
        type = ["json"],
        accept_multiple_files=False
    )
    
if st.session_state.do_translate:
    st.subheader("Translator Options")
    
    translator = st.pills(
        label = "Select a translator service.",
        options = ["Google", "DeepL"],
        default = "Google",
        key = "translator",
    )
    
    if translator == "Google":
        lang_list = list(MINECRAFT_TO_GOOGLE)
    elif translator == "DeepL":
        auth_key = st.text_input(
            label = Message("deepl_key_label").text,
            type = "password"
        )
        if auth_key:
            try:
                deepl_client = deepl.DeepLClient(auth_key)
                usage = deepl_client.get_usage()
                st.progress(usage.character.count / usage.character.limit, text=f"Characters used: {usage.character.count}/{usage.character.limit}")
            except:
                Message("deepl_key_error").warning()
        st.caption(Message("deepl_key_caption").text)
        lang_list = list(MINECRAFT_TO_DEEPL)
    
    source_lang = st.selectbox(
        label = Message("src_label").text,
        options = lang_list,
        index = lang_list.index("en_us"),
        format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
    )
    
    target_lang = st.selectbox(
        label = Message("dest_label").text,
        options = lang_list,
        index = lang_list.index("en_us"),
        format_func = lambda x: f"{x} ({MINECRAFT_LANGUAGES[x]})"
    )