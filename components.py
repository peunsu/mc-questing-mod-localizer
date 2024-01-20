import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from utils import localize_button, reset_localize_button
from constants import MINECRAFT_LANGUAGES, MESSAGES, MAX_FILES, MAX_CHARS

from typing import Iterator, Iterable, TYPE_CHECKING
if TYPE_CHECKING:
    from localizer import QuestLocalizer
    from streamlit.delta_generator import DeltaGenerator

class Message:
    """Message Class

    Args
    ----
        key (str): The key of the message.
        stop (bool, optional): If True, stop the app after showing the message. Defaults to False.
    
    Attributes
    ----------
        message (str): The formatted message.
        stop (bool): If True, stop the app after showing the message.
    """
    message: str
    stop: bool
    
    def __init__(self, key: str, stop: bool = False, **kwargs):
        self.message = MESSAGES[key].format(**kwargs)
        self.stop = stop
    
    def __repr__(self) -> str:
        return f"Message(message={self.message}, stop={self.stop})"
    
    def __str__(self) -> str:
        return self.message
    
    @property
    def text(self) -> str:
        """Get the message.

        Returns
        -------
            str: The formatted message.
        """
        return self.message
    
    def send(self) -> None:
        """Send the message.
        """
        st.write(self.message)
        if self.stop:
            st.stop()
    
    def info(self) -> None:
        """Show the message as an info message.
        """
        st.info(self.message, icon="ℹ️")
        if self.stop:
            st.stop()
    
    def warning(self) -> None:
        """Show the message as a warning message.
        """
        st.warning(self.message, icon="⚠️")
        if self.stop:
            st.stop()
    
    def error(self) -> None:
        """Show the message as an error message.
        """
        st.error(self.message, icon="❌")
        if self.stop:
            st.stop()
    
    def toast(self) -> None:
        """Show the message as a toast message.
        """
        st.toast(body=self.message, icon="📝")
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
        current (int): The current index of the iterable object.
        len (int): The length of the iterable object.
        iterator (Iterator): The iterator object of the iterable object.
        pbar (DeltaGenerator): The progress bar object.
        task (str): The task name.
    """
    current: int
    len: int
    iterator: Iterator
    pbar: "DeltaGenerator"
    task: str
    
    def __init__(self, iterable: Iterable, task: str) -> None:
        self.current = 0
        self.len = len(iterable)
        self.iterator = iter(iterable)
        self.pbar = st.progress(0)
        self.task = task
    
    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> tuple:
        element = next(self.iterator)
        self.current += 1
        progress = self.current / self.len
        
        if self.task == "convert":
            pbar_text = Message("convert_quests", progress=progress*100).text
        elif self.task == "translate":
            pbar_text = Message("translate_quests", progress=progress*100).text
            
        self.pbar.progress(progress, text=pbar_text)
        return element

class FileUploader:
    """File Uploader Class
    
    Args
    ----
        type (str): The type of the file to upload.
    
    Attributes
    ----------
        type (str): The type of the file to upload.
        files (list[BytesIO]): The uploaded files.
        label (str): The key of the label text of the file uploader.
        info (str): The key of the info text of the file uploader.
    """
    type: str
    files: list[BytesIO]
    label: str
    info: str
    
    def __init__(self, type: str) -> None:
        self.type = type
        self.files = []
        
        if self.type == "snbt":
            self.label = "uploader_snbt_label"
            self.info = "uploader_snbt_info"
    
    def __repr__(self) -> str:
        return f"FileUploader(type={self.type}, files={self.files}, label={self.label}, info={self.info})"
    
    def __str__(self) -> str:
        return self.__repr__()
        
    def show(self) -> None:
        """Show the file uploader.
        """
        self.files = st.file_uploader(
            label = Message(self.label).text,
            type = [self.type],
            accept_multiple_files = True,
            help = Message("uploader_help").text,
            on_change = reset_localize_button
        )
        if self.is_empty():
            Message(self.info, stop=True).info()
        elif self.is_exceed():
            Message("uploader_exceed", stop=True).error()
    
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
        return len(self.files) > MAX_FILES
    
class ModpackInput:
    """Modpack Input Class
    
    Attributes
    ----------
        text (str): The text input.
    """
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"ModpackInput(text={self.text})"
    
    def __str__(self) -> str:
        return self.text
    
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

class AutoTranslateRadio:
    """Auto Translate Radio Class
    """
    def __init__(self) -> None:
        pass
    
    def show(self) -> None:
        """Show the auto translate radio button.
        """
        st.radio(
            label = Message("auto_translate_label").text,
            options = [True, False],
            format_func = lambda x: "Yes" if x else "No",
            index = 1,
            help = Message("auto_translate_help").text,
            on_change = reset_localize_button,
            key = "translate"
        )

class LangSelectBox:
    """Language Select Box Class
    
    Args
    ----
        key (str): The key of the select box (src or dest).
    
    Attributes
    ----------
        key (str): The key of the select box (src or dest).
        label (str): The key of the label text of the select box.
        help (str): The key of the help text of the select box.
        disabled (bool): If True, disable the select box.
        lang (str): The selected language.
    """
    value: str
    label: str
    help: str
    disabled: bool
    lang: str
    
    def __init__(self, key: str) -> None:
        self.key = key
        if self.key == "src":
            self.label = "src_label"
            self.help = "src_help"
            self.disabled = False
        elif self.key == "dest":
            self.label = "dest_label"
            self.help = "dest_help"
            self.disabled = not st.session_state.translate
    
    def __repr__(self) -> str:
        return f"LangSelectBox(key={self.key}, label={self.label}, help={self.help}, disabled={self.disabled}, lang={self.lang})"
    
    def __str__(self) -> str:
        return self.lang
    
    def _lang_index(self, lang: str) -> int:
        return list(MINECRAFT_LANGUAGES).index(lang)

    def _lang_format(self, lang: str) -> str:
        return f"{lang} ({MINECRAFT_LANGUAGES[lang]})"
    
    def show(self) -> None:
        """Show the select box.
        """
        self.lang = st.selectbox(
            label = Message(self.label).text,
            options = MINECRAFT_LANGUAGES,
            index = self._lang_index("en_us"),
            format_func = self._lang_format,
            help = Message(self.help).text,
            on_change = reset_localize_button,
            disabled = self.disabled
        )

class LocalizeButton:
    """Localize Button Class
    """
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"LocalizeButton()"
    
    def __str__(self) -> str:
        return self.__repr__()
    
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
    
    def __repr__(self) -> str:
        return f"DownloadButton(data={self.data}, file_name={self.file_name})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
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

    def __repr__(self) -> str:
        return f"LangLinkButton()"
    
    def __str__(self) -> str:
        return self.__repr__()
    
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
    
    def __init__(self, localizer: "QuestLocalizer"):
        self.localizer = localizer
        self.src = localizer.src.lang
        self.dest = localizer.dest.lang
    
    def __repr__(self) -> str:
        return f"Manager(localizer={self.localizer}, src={self.src}, dest={self.dest})"

    def __str__(self) -> str:
        return self.__repr__()
    
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
            
    def download_snbt(self) -> None:
        """Show the download button for the localized SNBT files.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_name = "localized_snbt.zip"
            zip_dir = self.localizer.compress_quests(tmp_dir, zip_name)
            DownloadButton(BytesIO(open(zip_dir, "rb").read()), zip_name).show()
    
    def download_json(self, template: bool = False) -> None:
        """Show the download button for the localized JSON files.

        Args
        ----
            template (bool, optional): If True, download the template JSON file. Defaults to False.
        """
        if template:
            DownloadButton(BytesIO(self.localizer.template_json.encode("utf-8")), "template_lang.json").show()
            with st.expander(Message("show_json").text):
                st.json(self.localizer.template_json)
            return
        
        if st.session_state.translate:
            DownloadButton(BytesIO(self.localizer.src_json.encode("utf-8")), f"{self.src}.json").show()
            DownloadButton(BytesIO(self.localizer.dest_json.encode("utf-8")), f"{self.dest}.json").show()
            with st.expander(Message("show_json").text):
                tab1, tab2 = st.tabs([f"{self.src}.json", f"{self.dest}.json"])
                tab1.json(self.localizer.src_json)
                tab2.json(self.localizer.dest_json)
        else:
            DownloadButton(BytesIO(self.localizer.src_json.encode("utf-8")), f"{self.src}.json").show()
            with st.expander(Message("show_json").text):
                st.json(self.localizer.src_json)