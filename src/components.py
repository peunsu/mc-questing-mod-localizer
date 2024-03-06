import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from .utils import localize_button, reset_localize_button
from .constants import MINECRAFT_LANGUAGES, MESSAGES, MAX_FILES, MAX_CHARS, FTBQ, BQM

from typing import Iterator, Iterable, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from localizer import QuestLocalizer
    from streamlit.delta_generator import DeltaGenerator

__all__ = [
    "Message",
    "ProgressBar",
    "LanguageRadio",
    "FileUploader",
    "ModpackInput",
    "RadioButton",
    "LangSelectBox",
    "LocalizeButton",
    "DownloadButton",
    "LangLinkButton",
    "Manager"
]

class Message:
    """Message Class

    Args
    ----
        key (str): The key of the message.
        stop (bool, optional): If True, stop the app after showing the message. Defaults to False.
    
    Attributes
    ----------
        stop (bool): If True, stop the app after showing the message.
    """
    stop: bool
    
    _message: str
    
    def __init__(self, key: str, stop: bool = False, **kwargs):
        self._message = MESSAGES[st.query_params.lang][key].format(**kwargs)
        self.stop = stop
    
    @property
    def text(self) -> str:
        """Get the message.

        Returns
        -------
            str: The formatted message.
        """
        return self._message
    
    def send(self) -> None:
        """Send the message.
        """
        st.write(self._message)
        if self.stop:
            st.stop()
    
    def info(self) -> None:
        """Show the message as an info message.
        """
        st.info(self._message, icon="ℹ️")
        if self.stop:
            st.stop()
    
    def warning(self) -> None:
        """Show the message as a warning message.
        """
        st.warning(self._message, icon="⚠️")
        if self.stop:
            st.stop()
    
    def error(self) -> None:
        """Show the message as an error message.
        """
        st.error(self._message, icon="❌")
        if self.stop:
            st.stop()
    
    def toast(self) -> None:
        """Show the message as a toast message.
        """
        st.toast(body=self._message, icon="📝")
        if self.stop:
            st.stop()
            
class ProgressBar:
    """Progress Bar Class.
    Wraps an iterable object and shows a progress bar.

    Args
    ----
        iterable (Iterable): The iterable object.
        task (str): The task name.
    
    Attributes
    ----------
        task (str): The task name.
    """
    task: str
    
    _current: int
    _len: int
    _iterator: Iterator
    _pbar: "DeltaGenerator"
    
    def __init__(self, iterable: Iterable, task: str) -> None:
        self.task = task
        self._current = 0
        self._len = len(iterable)
        self._iterator = iter(iterable)
        self._pbar = st.progress(0)
    
    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> tuple:
        element = next(self._iterator)
        self._current += 1
        progress = self._current / self._len
        
        if self.task == "convert":
            pbar_text = Message("convert_quests", progress=progress*100).text
        elif self.task == "translate":
            pbar_text = Message("translate_quests", progress=progress*100).text
            
        self._pbar.progress(progress, text=pbar_text)
        return element

class LanguageRadio:
    """Language Radio Class
    
    Attributes
    ----------
        options (list[str]): The options of the radio button.
    """
    def __init__(self) -> None:
        self.options = ["en_us", "ko_kr"]
    
    def on_change(self) -> None:
        if "lang" in st.session_state:
            st.query_params.lang = st.session_state.lang
    
    def show(self) -> None:
        st.radio(
            label = "Site Language",
            options = self.options,
            format_func = lambda x: MINECRAFT_LANGUAGES[x],
            on_change = self.on_change,
            key = "lang"
        )

class FileUploader:
    """File Uploader Class
    
    Args
    ----
        type (str): The type of the file to upload.
    
    Attributes
    ----------
        type (str): The type of the file to upload. ("ftbq_quest", "bqm_quest", "ftbq_lang" or "bqm_lang")
        files (list[BytesIO]): The uploaded files.
    """
    type: str
    files: list[BytesIO]
    
    _info: str
    _ext: str
    
    def __init__(self, type: str) -> None:
        self.type = type
        self.files = []
        
        if self.type == "ftbq_quest":
            self._info = "uploader_ftbq_quest"
            self._ext = FTBQ["quest_ext"]
        elif self.type == "bqm_quest":
            self._info = "uploader_bqm_quest"
            self._ext = BQM["quest_ext"]
        elif self.type == "ftbq_lang":
            self._info = "uploader_ftbq_lang"
            self._ext = FTBQ["lang_ext"]
        elif self.type == "bqm_lang":
            self._info = "uploader_bqm_lang"
            self._ext = BQM["lang_ext"]
        
    def show(self) -> None:
        """Show the file uploader.
        """
        Message(self._info, max=MAX_FILES[self.type]).info()
        self.files = st.file_uploader(
            label = "Upload file(s).",
            type = [self._ext],
            accept_multiple_files = True,
            help = Message("uploader_help").text,
            on_change = reset_localize_button,
            label_visibility="collapsed"
        )
        if self.is_empty():
            st.stop()
        elif self.is_exceed():
            Message("uploader_exceed", max=MAX_FILES[self.type], stop=True).error()
    
    def is_empty(self) -> bool:
        """Check if the file uploader is empty.

        Returns
        -------
            bool: True if the file uploader is empty, False otherwise.
        """
        return not self.files

    def is_exceed(self) -> bool:
        """Check if the file uploader exceeds the maximum number of files.

        Returns
        -------
            bool: True if the file uploader exceeds the maximum number of files, False otherwise.
        """
        return len(self.files) > MAX_FILES[self.type]
    
class ModpackInput:
    """Modpack Input Class
    
    Attributes
    ----------
        text (str): The text input.
    """
    def __init__(self) -> None:
        pass
    
    def show(self) -> None:
        """Show the text input.
        """
        self.text = st.text_input(
            label = Message("modpack_label").text,
            max_chars = MAX_CHARS,
            help = Message("modpack_help").text,
            on_change = reset_localize_button
        )
        if self.is_empty():
            st.stop()
    
    def is_empty(self) -> bool:
        """Check if the text input is empty.

        Returns
        -------
            bool: True if the text input is empty, False otherwise.
        """
        return not self.text

class RadioButton:
    """Radio Button Class
    
    Args
    ----
        type (str): The type of the radio button.
        dir (str, optional): The directory of the language file. Defaults to None, only used for the "lang_exist" type.
        
    Attributes
    ----------
        type (str): The type of the radio button. ("lang_exist" or "auto_translate")
        lang_dir (str): The directory of the language file.
    """
    type: str
    lang_dir: str
    
    _label: str
    _help: str
    _on_change: Callable
    _key: str
    
    def __init__(self, type: str, lang_dir: str = None) -> None:
        self.type = type
        self.lang_dir = lang_dir
        if self.type == "lang_exist":
            self._label = "lang_exist_label"
            self._help = "lang_exist_help"
            self._on_change = None
            self._key = "lang_exist"
        elif self.type == "auto_translate":
            self._label = "auto_translate_label"
            self._help = "auto_translate_help"
            self._on_change = reset_localize_button
            self._key = "translate"
    
    def show(self) -> None:
        """Show the auto translate radio button.
        """
        st.radio(
            label = Message(self._label, lang_dir=self.lang_dir).text,
            options = [True, False],
            format_func = lambda x: "Yes" if x else "No",
            index = 1,
            help = Message(self._help).text,
            on_change = self._on_change,
            key = self._key
        )

class LangSelectBox:
    """Language Select Box Class
    
    Args
    ----
        key (str): The key of the select box (src or dest).
    
    Attributes
    ----------
        key (str): The key of the select box (src or dest).
        lang (str): The selected language.
    """
    key: str
    lang: str
    
    _label: str
    _help: str
    _disabled: bool
    
    def __init__(self, key: str) -> None:
        self.key = key
        self.lang = None
        if self.key == "src":
            self._label = "src_label"
            self._help = "src_help"
            self._disabled = False
        elif self.key == "dest":
            self._label = "dest_label"
            self._help = "dest_help"
            self._disabled = not st.session_state.translate
    
    def __str__(self) -> None:
        return self.lang
    
    def _lang_index(self, lang: str) -> int:
        return list(MINECRAFT_LANGUAGES).index(lang)

    def _lang_format(self, lang: str) -> str:
        return f"{lang} ({MINECRAFT_LANGUAGES[lang]})"
    
    def show(self) -> None:
        """Show the select box.
        """
        self.lang = st.selectbox(
            label = Message(self._label).text,
            options = MINECRAFT_LANGUAGES,
            index = self._lang_index("en_us"),
            format_func = self._lang_format,
            help = Message(self._help).text,
            on_change = reset_localize_button,
            disabled = self._disabled
        )

class LocalizeButton:
    """Localize Button Class
    """
    def __init__(self) -> None:
        pass
    
    def show(self):
        """Show the localize button.
        """
        st.button(
            label = Message("localize_label").text,
            help = Message("localize_help").text,
            on_click = localize_button,
            disabled = st.session_state.localize
        )

class DownloadButton:
    """Download Button Class
    
    Args
    ----
        data (BytesIO): The data to download.
        file_name (str): The name of the file to download.
    
    Attributes
    ----------
        data (BytesIO): The data to download.
        file_name (str): The name of the file to download.
    """
    data: BytesIO
    file_name: str
    
    def __init__(self, data: BytesIO, file_name: str) -> None:
        self.data = data
        self.file_name = file_name
    
    def show(self) -> None:
        ste.download_button(
            label = Message("download_button", file_name=self.file_name).text,
            data = self.data,
            file_name = self.file_name,
            mime = "application/octet-stream"
        )
    
class LangLinkButton:
    """Language Link Button Class
    """
    def __init__(self) -> None:
        pass
    
    def show(self) -> None:
        """Show the language link button.
        """
        st.link_button(
            label = Message("lang_link_label").text,
            url = Message("lang_link_url").text,
            help = Message("lang_link_help").text
        )

class Manager:
    """FTB Quests Localization Manager Class
    
    Args
    ----
        localizer (QuestLocalizer): The QuestLocalizer object.
    
    Attributes
    ----------
        localizer (QuestLocalizer): The QuestLocalizer object.
        src (str): The source language.
        dest (str): The destination language.
    """
    localizer: "QuestLocalizer"
    src: str
    dest: str
    
    _class: str
    _ext: str
    
    def __init__(self, localizer: "QuestLocalizer"):
        self.localizer = localizer
        self.src = localizer.src.lang
        self.dest = localizer.dest.lang
        self._class = localizer.__class__.__name__
        
        if self._class == "FTBQuestLocalizer":
            self._ext = FTBQ["lang_ext"]
        elif self._class == "BQMQuestLocalizer":
            self._ext = BQM["lang_ext"]
    
    def run(self) -> None:
        """Run the localization.
        """
        self._convert()
        if st.session_state.translate:
            self._translate()
    
    def _convert(self) -> None:
        try:
            self.localizer.convert_quests()
            Message("convert_success").toast()
        except Exception as e:
            st.write(e)
            Message("convert_error", stop=True, e=e).error()
    
    def _translate(self) -> None:
        if self.src == self.dest:
            Message("translate_same_lang", stop=True).error()
        try:
            self.localizer.translate_quests()
            Message("translate_success").toast()
        except Exception as e:
            Message("translate_error", stop=True, e=e).error()

    def download_quest(self) -> None:
        """Show the download button for the localized quest file.
        """
        if self._class == "FTBQuestLocalizer":
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_name = FTBQ["filename"]
                zip_dir = self.localizer.compress_quests(tmp_dir, zip_name)
                DownloadButton(BytesIO(open(zip_dir, "rb").read()), zip_name).show()
        elif self._class == "BQMQuestLocalizer":
            DownloadButton(BytesIO(self.localizer.quest_json.encode("utf-8")), BQM["filename"]).show()
            
    def download_lang(self, type: str) -> None:
        """Show the download button for the localized language files.

        Args
        ----
            type (str): The type of the LANG file to download. ("src", "dest", "both" or "template")
        """
        src_filename = f"{self.src}.{self._ext}"
        dest_filename = f"{self.dest}.{self._ext}"
        template_filename = f"template.{self._ext}"
        
        if type == "src":
            DownloadButton(BytesIO(self.localizer.src_lang.encode("utf-8")), src_filename).show()
        elif type == "dest":
            DownloadButton(BytesIO(self.localizer.dest_lang.encode("utf-8")), dest_filename).show()
        elif type == "both":
            DownloadButton(BytesIO(self.localizer.src_lang.encode("utf-8")), src_filename).show()
            DownloadButton(BytesIO(self.localizer.dest_lang.encode("utf-8")), dest_filename).show()
        elif type == "template":
            DownloadButton(BytesIO(self.localizer.template_lang.encode("utf-8")), template_filename).show()