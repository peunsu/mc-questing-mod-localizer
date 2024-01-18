import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from localizer import QuestLocalizer
from constants import MINECRAFT_LANGUAGES, MESSAGES, MAX_FILES, MAX_CHARS

if 'localize' not in st.session_state:
    st.session_state.localize = False

def localize_button() -> None:
    st.session_state.localize = True

def reset_localize_button() -> None:
    st.session_state.localize = False
    
def lang_index(lang: str) -> int:
    return list(MINECRAFT_LANGUAGES).index(lang)

def lang_format(lang: str) -> str:
    return f"{lang} ({MINECRAFT_LANGUAGES[lang]})"

class Message:
    message: str
    stop: bool
    
    def __init__(self, key: str, stop: bool = False, **kwargs):
        self.message = MESSAGES[key].format(**kwargs)
        self.stop = stop
    
    def text(self) -> str:
        return self.message
    
    def send(self) -> None:
        st.write(self.message)
        if self.stop:
            st.stop()
    
    def info(self) -> None:
        st.info(self.message, icon="ℹ️")
        if self.stop:
            st.stop()
    
    def warning(self) -> None:
        st.warning(self.message, icon="⚠️")
        if self.stop:
            st.stop()
    
    def error(self) -> None:
        st.error(self.message, icon="❌")
        if self.stop:
            st.stop()

def show_toast_message(message: str) -> None:
    st.toast(body=message, icon="📝")

class ProgressBar:
    localizer: QuestLocalizer
    
    def __init__(self, localizer: QuestLocalizer):
        self.localizer = localizer
    
    def run(self) -> None:
        self._convert()
        if st.session_state.translate:
            self._translate()
    
    def _convert(self) -> None:
        convert_bar_text = MESSAGES["convert_quests"]
        convert_bar = st.progress(0, text=convert_bar_text)
        try:
            self.localizer.convert_quests(convert_bar, convert_bar_text)
            convert_bar.progress(1.0, text=MESSAGES["convert_success"])
        except Exception as e:
            Message("convert_error", stop=True, e=e).error()
    
    def _translate(self) -> None:
        translate_bar_text = MESSAGES["translate_quests"]
        translate_bar = st.progress(0, text=translate_bar_text)
        try:
            self.localizer.translate_quests(translate_bar, translate_bar_text)
            translate_bar.progress(1.0, text=MESSAGES["translate_success"])
        except Exception as e:
            Message("translate_error", stop=True, e=e).error()

class DownloadButton:
    localizer: QuestLocalizer
    src: str
    dest: str
    
    def __init__(self, localizer: QuestLocalizer):
        self.localizer = localizer
        self.src = localizer.src_lang.lang
        self.dest = localizer.dest_lang.lang
    
    def show(self, data: BytesIO, file_name: str) -> None:
        ste.download_button(
            label = MESSAGES["download_button"].format(file_name=file_name),
            data = data,
            file_name = file_name,
            mime = "application/octet-stream"
        )
    
    def snbt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_dir = self.localizer.compress_quests(tmp_dir)
            self.show(BytesIO(open(zip_dir, "rb").read()), "localized_snbt.zip")
    
    def json(self, template: bool = False) -> None:
        if template:
            self.show(BytesIO(self.localizer.template_json.encode("utf-8")), "template_lang.json")
            with st.expander("Show JSON"):
                st.json(self.localizer.template_json)
            return
        
        if st.session_state.translate:
            self.show(BytesIO(self.localizer.src_json.encode("utf-8")), f"{self.src}.json")
            self.show(BytesIO(self.localizer.dest_json.encode("utf-8")), f"{self.dest}.json")
            with st.expander("Show JSON"):
                tab1, tab2 = st.tabs([f"{self.src}.json", f"{self.dest}.json"])
                tab1.json(self.localizer.src_json)
                tab2.json(self.localizer.dest_json)
        else:
            self.show(BytesIO(self.localizer.src_json.encode("utf-8")), f"{self.src}.json")
            with st.expander("Show JSON"):
                st.json(self.localizer.src_json)
                
st.set_page_config(
    page_title="FTB Quests Localization Tool",
    page_icon="📝",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/peunsu/ftbq-localization-tool",
        "Report a Bug": "https://github.com/peunsu/ftbq-localization-tool/issues",
        "About": '''
        ### FTB Quests Localization Tool\n
        Release v1.1.0 ([GitHub](https://github.com/peunsu/ftbq-localization-tool))\n
        Created by [peunsu](https://github.com/peunsu).\n
        [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) by [FTB Team](https://www.curseforge.com/members/ftb).\n
        '''
    }
)

st.title("FTB Quests Localization Tool")

st.subheader("Upload FTB Quests Files")

uploaded_files = st.file_uploader(
    label = Message("uploader_label").text(),
    type = ["snbt"],
    accept_multiple_files = True,
    help = Message("uploader_help").text(),
    on_change = reset_localize_button,
)
if not uploaded_files:
    Message("uploader_empty", stop=True).info()
if len(uploaded_files) > MAX_FILES:
    Message("uploader_exceed", stop=True).error()

st.subheader("Modpack Name")

modpack = st.text_input(
    label = Message("modpack_label").text(),
    value = "modpack",
    max_chars = MAX_CHARS,
    help = Message("modpack_help").text(),
    on_change = reset_localize_button
)

st.subheader("Auto Translate")

st.radio(
    label = Message("auto_translate_label").text(),
    options = [True, False],
    format_func = lambda x: "Yes" if x else "No",
    index = 1,
    help = Message("auto_translate_help").text(),
    on_change = reset_localize_button,
    key = "translate"
)

src = st.selectbox(
    label = Message("src_label").text(),
    options = MINECRAFT_LANGUAGES,
    index = lang_index("en_us"),
    format_func = lang_format,
    help = Message("src_help").text(),
    on_change = reset_localize_button
)

dest = st.selectbox(
    label = Message("dest_label").text(),
    options = MINECRAFT_LANGUAGES,
    index = lang_index("en_us") if st.session_state.translate else lang_index(src),
    format_func = lang_format,
    help = Message("dest_help").text(),
    on_change = reset_localize_button,
    disabled = not st.session_state.translate
)

st.subheader("Localize!")

localizer = QuestLocalizer(uploaded_files, src, dest, modpack)

st.button(
    label = Message("localize_label").text(),
    help = Message("localize_help").text(),
    on_click = localize_button,
    disabled = st.session_state.localize
)

if st.session_state.localize:
    progress_bar = ProgressBar(localizer)
    
    show_toast_message(Message("localize_start").text())
    progress_bar.run()
    show_toast_message(Message("localize_finish").text())
    
    
    st.subheader("How to Apply Localization")
    
    download_button = DownloadButton(localizer)
    
    Message("apply_manual_1").send()
    download_button.snbt()
    Message("apply_manual_2").send()
    if st.session_state.translate:
        Message("apply_manual_3_1", src=src, dest=dest).send()
        download_button.json()
        Message("apply_manual_4_1", src=src, dest=dest).send()
        Message("apply_manual_5_1", dest=dest).send()
        Message("apply_manual_warning", src=src).warning()
    else:
        Message("apply_manual_3_2", src=src).send()
        download_button.json()
        Message("apply_manual_4_2", src=src).send()
        Message("apply_manual_5_2").send()
    
    st.subheader("How to Add New Language Manually")
    
    Message("add_manual_1").send()
    download_button.json(template=True)
    Message("add_manual_2").send()
    st.link_button(
        label = Message("lang_link_label").text(),
        url = Message("lang_link_url").text(),
        help = Message("lang_link_help").text()
    )
    Message("add_manual_3", src=src).send()
    Message("add_manual_warning", src=src).warning()
    Message("add_manual_4").send()
    Message("add_manual_5").send()