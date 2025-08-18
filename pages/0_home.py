import streamlit as st
from src.utils import Message

st.title(Message("home_title").text)

st.page_link("pages/1_ftbq.py", label=Message("ftbq_title").text, icon="👑")
st.page_link("pages/2_ftbq_new.py", label=Message("ftbq_new_title").text, icon="⭐")
st.page_link("pages/3_bqm.py", label=Message("bqm_title").text, icon="📖")
st.page_link("pages/4_translation_fixer.py", label=Message("translation_fixer_title").text, icon="🛠️")

st.divider()

st.subheader("About")
st.write("[![GitHub Release](https://img.shields.io/github/v/release/peunsu/mc-questing-mod-localizer?style=for-the-badge)](https://github.com/peunsu/mc-questing-mod-localizer/releases/latest)")
st.write(Message("home_about").text)

st.subheader(Message("home_new_title").text)
st.write(Message("home_new_desc").text)

st.subheader(Message("home_contact_title").text)
st.write("* [GitHub](https://github.com/peunsu/mc-questing-mod-localizer)")
st.write("* [Email](mailto:peunsu55@gmail.com)")

st.subheader("License")
st.write("[MIT License](https://github.com/peunsu/mc-questing-mod-localizer/blob/main/LICENSE) ⓒ 2024-2025 [peunsu](https://github.com/peunsu)")
