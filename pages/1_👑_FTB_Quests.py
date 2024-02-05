import streamlit as st

from src import localize_init, language_init, set_page_config, FTBQuestLocalizer
from src.components import *
from src.constants import FTBQ

localize_init()
language_init()

set_page_config(
    title = "FTB Quests Localizer",
    icon = "https://media.forgecdn.net/avatars/275/363/637261948352026071.png"
)

with st.sidebar:
    LanguageRadio().show()

st.title(Message("ftbq_title").text)
st.page_link("Home.py", label=Message("back_to_home").text, icon="↩️")

st.divider()

st.subheader(Message("header_lang_check").text)
RadioButton("lang_exist", lang_dir=FTBQ["lang_dir"]).show()
Message("lang_exist_warning").warning()

if st.session_state.lang_exist:
    st.subheader(Message("header_upload").text)
    uploader = FileUploader("ftbq_lang")
    uploader.show()
else:
    st.subheader(Message("header_upload").text)
    uploader = FileUploader("ftbq_quest")
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
    localizer = FTBQuestLocalizer(uploader.files, src.lang, dest.lang, None, translate_only=True)
    LocalizeButton().show()
else:
    st.subheader(Message("header_localize").text)
    localizer = FTBQuestLocalizer(uploader.files, src.lang, dest.lang, modpack_input.text)
    LocalizeButton().show()

if st.session_state.localize:
    manager = Manager(localizer)
    manager.run()
    
    st.divider()
    
    if st.session_state.lang_exist:
        if st.session_state.translate:
            st.subheader(Message("header_apply_manual").text)
            Message("apply_manual_lang_1", dest=dest, **FTBQ).send()
            manager.download_lang("dest")
            Message("apply_manual_lang_2", src=src, dest=dest, **FTBQ).send()
            Message("apply_manual_lang_3", dest=dest, **FTBQ).send()
            Message("apply_manual_warning", src=src, **FTBQ).warning()
    else:
        st.subheader(Message("header_apply_manual").text)
        Message("apply_manual_1", **FTBQ).send()
        manager.download_quest()
        Message("apply_manual_2_1", **FTBQ).send()
        if st.session_state.translate:
            Message("apply_manual_3_1", src=src, dest=dest, **FTBQ).send()
            manager.download_lang("both")
            Message("apply_manual_4_1", src=src, dest=dest, **FTBQ).send()
            Message("apply_manual_5_1", dest=dest, **FTBQ).send()
        else:
            Message("apply_manual_3_2", src=src, **FTBQ).send()
            manager.download_lang("src")
            Message("apply_manual_4_2", src=src, **FTBQ).send()
            Message("apply_manual_5_2").send()
        Message("apply_manual_warning", src=src, **FTBQ).warning()
    
    st.subheader(Message("header_add_manual").text)
    Message("add_manual_1", **FTBQ).send()
    manager.download_lang("template")
    Message("add_manual_2", **FTBQ).send()
    LangLinkButton().show()
    Message("add_manual_3", src=src, **FTBQ).send()
    Message("add_manual_warning", src=src, **FTBQ).warning()
    Message("add_manual_4", src=src, **FTBQ).send()
    Message("add_manual_5").send()