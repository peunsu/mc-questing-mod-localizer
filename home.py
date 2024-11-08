import streamlit as st
from src.components import Message

st.title(Message("home_title").text)

st.page_link("localizers/1_ftbq.py", label="FTB Quests", icon="👑")
st.page_link("localizers/2_ftbq_renewal.py", label="FTB Quests 1.21+ (Beta)", icon="⭐")
st.page_link("localizers/3_bqm.py", label="Better Questing", icon="📖")

st.divider()

st.subheader("About")
st.write("[![GitHub Release](https://img.shields.io/github/v/release/peunsu/mc-questing-mod-localizer?style=for-the-badge)](https://github.com/peunsu/mc-questing-mod-localizer/releases/latest)")
st.write(Message("home_about").text)

st.subheader(Message("home_new_title").text)
st.write(Message("home_new_desc").text)

st.subheader(Message("home_contact_title").text)
st.write("* [GitHub](https://github.com/peunsu/mc-questing-mod-localizer)")
st.write("* [Discord Server (Mystic Red Space)](https://discord.gg/Z8j6ahF4MJ)")
st.write("* [Email](mailto:peunsu55@gmail.com)")

st.subheader("License")
st.write("[MIT License](https://github.com/peunsu/mc-questing-mod-localizer/blob/main/LICENSE) ⓒ 2024 [peunsu](https://github.com/peunsu)")
