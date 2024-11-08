import time
import streamlit as st

from src.utils import *
from src.localizer import FTBRenewalLocalizer, Translator
from src.components import *

localize_init()
translator_init()

st.session_state.translate_only = True
st.session_state.translate = True

with st.sidebar:
    TranslatorRadio().show()
    deepl_key_input = DeepLKeyInput()
    deepl_key_input.show()

Message("ftbq_renewal_title").title()
HomeButton().show()

st.divider()

st.subheader(Message("home_new_title").text)
st.write(Message("home_new_desc").text)

st.divider()

locale_uploader = FTBRenewalLocaleUploader()
locale_uploader.show()

src_sb = SrcLangSelectBox()
src_sb.show()
dest_sb = DestLangSelectBox()
dest_sb.show()

Message("header_localize").subheader()
if st.session_state.translator == "DeepL" and not deepl_key_input.validate_key():
    Message("deepl_key_check", stop=True).warning()

with st.spinner('Loading...'):
    translator = Translator().get_translator(st.session_state.translator, deepl_key_input.auth_key)
    localizer = FTBRenewalLocalizer(locale_uploader.files, None, translator, src_sb.lang, dest_sb.lang, None)
    time.sleep(2)
LocalizeButton().show()

if st.session_state.localize:
    manager = FTBRenewalLocalizerManager(localizer)
    manager.run()
    manager.show_manual()