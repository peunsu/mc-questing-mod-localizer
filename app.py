import streamlit as st

from utils import localize_init
from localizer import QuestLocalizer
from components import *

VERSION = "1.2.1"

localize_init()

st.set_page_config(
    page_title="FTB Quests Localization Tool",
    page_icon="https://media.forgecdn.net/avatars/275/363/637261948352026071.png",
    menu_items={
        "Get help": "https://github.com/peunsu/ftbq-localization-tool",
        "Report a Bug": "https://github.com/peunsu/ftbq-localization-tool/issues",
        "About": '''
        ### FTB Quests Localization Tool\n
        Release v{VERSION} ([GitHub](https://github.com/peunsu/ftbq-localization-tool))\n
        Created by [peunsu](https://github.com/peunsu).\n
        [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).\n
        '''.format(VERSION=VERSION)
    }
)

st.title("FTB Quests Localization Tool")
st.caption("Version {VERSION}".format(VERSION=VERSION))

st.subheader("Upload FTB Quests Files")

snbt_uploader = FileUploader("snbt")
snbt_uploader.show()

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

localizer = QuestLocalizer(snbt_uploader.files, src.lang, dest.lang, modpack_input.text)

LocalizeButton().show()

if st.session_state.localize:
    manager = Manager(localizer)
    manager.run()
    
    st.subheader("How to Apply Localization")
    
    Message("apply_manual_1").send()
    manager.download_snbt()
    Message("apply_manual_2").send()
    if st.session_state.translate:
        Message("apply_manual_3_1", src=src, dest=dest).send()
        manager.download_json()
        Message("apply_manual_4_1", src=src, dest=dest).send()
        Message("apply_manual_5_1", dest=dest).send()
    else:
        Message("apply_manual_3_2", src=src).send()
        manager.download_json()
        Message("apply_manual_4_2", src=src).send()
        Message("apply_manual_5_2").send()
    Message("apply_manual_warning", src=src).warning()
    
    st.subheader("How to Add New Language Manually")
    
    Message("add_manual_1").send()
    manager.download_json(template=True)
    Message("add_manual_2").send()
    LangLinkButton().show()
    Message("add_manual_3", src=src).send()
    Message("add_manual_warning", src=src).warning()
    Message("add_manual_4").send()
    Message("add_manual_5").send()