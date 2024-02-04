import streamlit as st

from src import localize_init, language_init, set_page_config, FTBQuestLocalizer
from src.components import *

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

st.subheader(Message("header_upload").text)
snbt_uploader = FileUploader("snbt")
snbt_uploader.show()

st.subheader(Message("header_modpack_name").text)
modpack_input = ModpackInput()
modpack_input.show()

st.subheader(Message("header_auto_translate").text)
AutoTranslateRadio().show()
src = LangSelectBox("src")
src.show()
dest = LangSelectBox("dest")
dest.show()

st.subheader(Message("header_localize").text)
localizer = FTBQuestLocalizer(snbt_uploader.files, src.lang, dest.lang, modpack_input.text)
LocalizeButton().show()

if st.session_state.localize:
    manager = Manager(localizer)
    manager.run()
    
    st.divider()
    
    st.subheader(Message("header_apply_manual").text)
    Message("apply_manual_1", filename="localized_snbt.zip").send()
    manager.download_snbt()
    Message("apply_manual_2_1", filename="localized_snbt.zip", ext="snbt", dir="config/ftbquests/quests").send()
    if st.session_state.translate:
        Message("apply_manual_3_1", src=src, dest=dest, ext="json").send()
        manager.download_json()
        Message("apply_manual_4_1", src=src, dest=dest, ext="json", dir="kubejs/assets/kubejs/lang").send()
        Message("apply_manual_5_1", dest=dest, ext="json").send()
    else:
        Message("apply_manual_3_2", src=src, ext="json").send()
        manager.download_json()
        Message("apply_manual_4_2", src=src, ext="json", dir="kubejs/assets/kubejs/lang").send()
        Message("apply_manual_5_2").send()
    Message("apply_manual_warning", src=src, ext="json", example="modpack.chapter.title.0.0").warning()
    
    st.subheader(Message("header_add_manual").text)
    Message("add_manual_1", ext="json").send()
    manager.download_json(template=True)
    Message("add_manual_2", ext="json").send()
    LangLinkButton().show()
    Message("add_manual_3", src=src, ext="json").send()
    Message("add_manual_warning", src=src, ext="json").warning()
    Message("add_manual_4", ext="json", dir="kubejs/assets/kubejs/lang").send()
    Message("add_manual_5").send()