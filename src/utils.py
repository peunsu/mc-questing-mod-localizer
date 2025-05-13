from io import StringIO, BytesIO
import streamlit as st

def localize_init() -> None:
    if 'localize' not in st.session_state:
        st.session_state.localize = False
        
def language_init() -> None:
    if "lang" not in st.query_params:
        st.query_params.lang = "en_us"

def translator_init() -> None:
    if "translator" not in st.session_state:
        st.session_state.translator = "Google"

def localize_button() -> None:
    st.session_state.localize = True

def reset_localize_button(*args) -> None:
    st.session_state.localize = False

def read_file(file: BytesIO) -> str:
    try:
        return StringIO(file.getvalue().decode('utf-8')).read()
    except UnicodeDecodeError:
        return StringIO(file.getvalue().decode('ISO-8859-1')).read()