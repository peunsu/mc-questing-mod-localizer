import streamlit as st

from src.utils import *
from src.localizer import BQMLocalizer
from src.components import *

localize_init()
language_init()

set_page_config(
    title = "Better Questing Localizer",
    icon = "https://media.forgecdn.net/avatars/30/140/635857624698238672.png"
)

LanguageRadio().show()

Message("bqm_title").title()
HomeButton().show()

st.divider()

BQMSelectTaskRadio().show()
    
st.divider()

modpack_input = ModpackInput()
modpack_input.show()

locale_uploader = BQMLocaleUploader()
quest_uploader = BQMQuestUploader()

if st.session_state.translate_only:
    locale_uploader.show()
else:
    BQMLangExistRadio().show()
    if st.session_state.lang_exist:
        locale_uploader.show()
    quest_uploader.show()

src_sb = SrcLangSelectBox()
src_sb.show()
dest_sb = DestLangSelectBox()
dest_sb.show()

Message("header_localize").subheader()
localizer = BQMLocalizer(locale_uploader.files, quest_uploader.files, src_sb.lang, dest_sb.lang, modpack_input.text)
LocalizeButton().show()

if st.session_state.localize:
    manager = BQMLocalizerManager(localizer)
    manager.run()
    manager.show_manual()