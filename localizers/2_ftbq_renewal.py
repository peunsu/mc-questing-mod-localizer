import streamlit as st

from src.utils import *
from src.components import *

localize_init()
translator_init()

with st.sidebar:
    TranslatorRadio().show()
    deepl_key_input = DeepLKeyInput()
    deepl_key_input.show()

Message("ftbq_renewal_title").title()
HomeButton().show()

st.divider()

st.subheader(Message("home_new_title").text)
st.write(Message("home_new_desc").text)