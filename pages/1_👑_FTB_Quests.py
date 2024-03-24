import streamlit as st

from src.utils import *
from src.localizer import FTBLocalizer
from src.components import *

localize_init()
language_init()

set_page_config(
    title = "FTB Quests Localizer",
    icon = "https://media.forgecdn.net/avatars/275/363/637261948352026071.png"
)

LanguageRadio().show()

Message("ftbq_title").title()
HomeButton().show()

st.divider()

FTBSelectTaskRadio().show()
    
st.divider()

modpack_input = ModpackInput()
modpack_input.show()

locale_uploader = FTBLocaleUploader()
quest_uploader = FTBQuestUploader()

if st.session_state.translate_only:
    locale_uploader.show()
else:
    FTBLangExistRadio().show()
    if st.session_state.lang_exist:
        locale_uploader.show()
    quest_uploader.show()

src_sb = SrcLangSelectBox()
src_sb.show()
dest_sb = DestLangSelectBox()
dest_sb.show()

Message("header_localize").subheader()
localizer = FTBLocalizer(locale_uploader.files, quest_uploader.files, src_sb.lang, dest_sb.lang, modpack_input.text)
LocalizeButton().show()

if st.session_state.localize:
    manager = FTBLocalizerManager(localizer)
    manager.run()
    manager.show_manual()