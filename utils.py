import streamlit as st

def localize_init() -> None:
    """Initialize the session state "localize" to False.
    """
    if 'localize' not in st.session_state:
        st.session_state.localize = False

def localize_button() -> None:
    """Set the session state "localize" to True.
    """
    st.session_state.localize = True

def reset_localize_button() -> None:
    """Set the session state "localize" to False.
    """
    st.session_state.localize = False