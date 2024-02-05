import streamlit as st

from src import localize_init, language_init, set_page_config, BQMQuestLocalizer
from src.components import *
from src.constants import BQM

localize_init()
language_init()

set_page_config(
    title = "Better Questing Localizer",
    icon = "https://media.forgecdn.net/avatars/30/140/635857624698238672.png"
)

with st.sidebar:
    LanguageRadio().show()

st.title(Message("bq_title").text)
st.page_link("Home.py", label=Message("back_to_home").text, icon="↩️")

st.divider()

st.subheader(Message("header_lang_check").text)
RadioButton("lang_exist", lang_dir=BQM["lang_dir"]).show()
Message("lang_exist_warning").warning()

if st.session_state.lang_exist:
    st.subheader(Message("header_upload").text)
    uploader = FileUploader("bqm_lang")
    uploader.show()
else:
    st.subheader(Message("header_upload").text)
    uploader = FileUploader("bqm_quest")
    uploader.show()

    st.subheader(Message("header_modpack_name").text)
    modpack_input = ModpackInput()
    modpack_input.show()

st.subheader(Message("header_auto_translate").text)
RadioButton("auto_translate").show()
src = LangSelectBox("src")
src.show()
dest = LangSelectBox("dest")
dest.show()

if st.session_state.lang_exist:
    st.subheader(Message("header_localize").text)
    localizer = BQMQuestLocalizer(uploader.files, src.lang, dest.lang, None, translate_only=True)
    LocalizeButton().show()
else:
    st.subheader(Message("header_localize").text)
    localizer = BQMQuestLocalizer(uploader.files, src.lang, dest.lang, modpack_input.text)
    LocalizeButton().show()

if st.session_state.localize:
    manager = Manager(localizer)
    manager.run()
    
    st.divider()
    
    if st.session_state.lang_exist:
        if st.session_state.translate:
            st.subheader(Message("header_apply_manual").text)
            Message("apply_manual_lang_1", dest=dest, **BQM).send()
            manager.download_lang("dest")
            Message("apply_manual_lang_2", src=src, dest=dest, **BQM).send()
            Message("apply_manual_lang_3", dest=dest, **BQM).send()
            Message("apply_manual_warning", src=src, **BQM).warning()
    else:
        st.subheader(Message("header_apply_manual").text)
        Message("apply_manual_1", filename="DefaultQuests.json").send()
        manager.download_quest()
        Message("apply_manual_2_1", filename="DefaultQuests.json", **BQM).send()
        if st.session_state.translate:
            Message("apply_manual_3_1", src=src, dest=dest, **BQM).send()
            manager.download_lang("both")
            Message("apply_manual_4_1", src=src, dest=dest, **BQM).send()
            Message("apply_manual_5_1", dest=dest, **BQM).send()
        else:
            Message("apply_manual_3_2", src=src, **BQM).send()
            manager.download_lang("src")
            Message("apply_manual_4_2", src=src,**BQM).send()
            Message("apply_manual_5_2").send()
        Message("apply_manual_warning", src=src, **BQM).warning()
    
    st.subheader(Message("header_add_manual").text)
    Message("add_manual_1", **BQM).send()
    manager.download_lang("template")
    Message("add_manual_2", **BQM).send()
    LangLinkButton().show()
    Message("add_manual_3", src=src, **BQM).send()
    Message("add_manual_warning", src=src, **BQM).warning()
    Message("add_manual_4", src=src, **BQM).send()
    Message("add_manual_5").send()