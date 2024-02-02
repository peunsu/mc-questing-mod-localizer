import streamlit as st

from utils import localize_init, set_page_config
from localizer import BQMQuestLocalizer
from components import *

localize_init()

set_page_config(
    title = "Better Questing Localizer",
    icon = "https://media.forgecdn.net/avatars/30/140/635857624698238672.png"
)

st.title("Better Questing Localizer")
st.caption(Message("version").text)

st.page_link("Home.py", label="Back to Home", icon="↩️")

st.subheader("Upload Quest File")

json_uploader = FileUploader("json")
json_uploader.show()

st.subheader("Modpack Name")

modpack_input = ModpackInput()
modpack_input.show()

st.subheader("Auto Translate")

AutoTranslateRadio().show()

src = LangSelectBox("src")
src.show()

dest = LangSelectBox("dest")
dest.show()

st.subheader("Localize!")

localizer = BQMQuestLocalizer(json_uploader.files, src.lang, dest.lang, modpack_input.text)

LocalizeButton().show()

if st.session_state.localize:
    manager = Manager(localizer)
    manager.run()
    
    st.subheader("How to Apply Localization")
    
    Message("apply_manual_1", filename="DefaultQuests.json").send()
    manager.download_bqm()
    Message("apply_manual_2_2", filename="DefaultQuests.json", ext="json", dir="config/betterquesting").send()
    if st.session_state.translate:
        Message("apply_manual_3_1", src=src, dest=dest, ext="lang").send()
        manager.download_lang()
        Message("apply_manual_4_1", src=src, dest=dest, ext="lang", dir="resources/betterquesting/lang").send()
        Message("apply_manual_5_1", dest=dest, ext="lang").send()
    else:
        Message("apply_manual_3_2", src=src, ext="lang").send()
        manager.download_lang()
        Message("apply_manual_4_2", src=src, ext="lang", dir="resources/betterquesting/lang").send()
        Message("apply_manual_5_2").send()
    Message("apply_manual_warning", src=src, ext="lang", example="modpack.quest.0.name").warning()
    
    st.subheader("How to Add New Language Manually")
    
    Message("add_manual_1", ext="lang").send()
    manager.download_lang(template=True)
    Message("add_manual_2", ext="lang").send()
    LangLinkButton().show()
    Message("add_manual_3", src=src, ext="lang").send()
    Message("add_manual_warning", src=src, ext="lang").warning()
    Message("add_manual_4", ext="lang", dir="resources/betterquesting/lang").send()
    Message("add_manual_5").send()