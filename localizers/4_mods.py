import time
import streamlit as st

from src.utils import *
from src.localizer import FTBLocalizer, Translator
from src.components import *

localize_init()
translator_init()

st.session_state.translate_only = True
st.session_state.translate = True

with st.sidebar:
    TranslatorRadio().show()
    deepl_key_input = DeepLKeyInput()
    deepl_key_input.show()
    
Message("mods_title").title()
HomeButton().show()

st.divider()

st.header("Winter is coming...")

st.info("This page is still under development. Please be patient.", icon="⏳")

st.snow()