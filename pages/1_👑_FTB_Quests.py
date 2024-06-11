import time
import streamlit as st

from src.utils import *
from src.localizer import FTBLocalizer, Translator
from src.components import *

localize_init()
language_init()
translator_init()

set_page_config(
    title = "FTB Quests Localizer",
    icon = "https://media.forgecdn.net/avatars/275/363/637261948352026071.png"
)

with st.sidebar:
    LanguageRadio().show()
    TranslatorRadio().show()
    deepl_key_input = DeepLKeyInput()
    deepl_key_input.show()

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
if not is_key_valid(deepl_key_input.auth_key):
    Message("deepl_key_check", stop=True).warning()
    
with st.spinner('Loading...'):
    translator = Translator().get_translator(st.session_state.translator, deepl_key_input.auth_key)
    localizer = FTBLocalizer(locale_uploader.files, quest_uploader.files, translator, src_sb.lang, dest_sb.lang, modpack_input.text)
    time.sleep(2)
LocalizeButton().show()

if st.session_state.localize:
    manager = FTBLocalizerManager(localizer)
    manager.run()
    manager.show_manual()