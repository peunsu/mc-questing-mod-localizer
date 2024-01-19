from __future__ import annotations

import tempfile
import streamlit as st
import streamlit_ext as ste

from io import BytesIO
from constants import MESSAGES, MINECRAFT_LANGUAGES

from typing import Iterator, Iterable, TYPE_CHECKING
if TYPE_CHECKING:
    from localizer import QuestLocalizer
    from streamlit.delta_generator import DeltaGenerator

def lang_index(lang: str) -> int:
    """Get the index of the language in the list of Minecraft languages.

    Args
    ----
        lang (str): The language.

    Returns
    -------
        int: The index of the language in the list of Minecraft languages.
    """
    return list(MINECRAFT_LANGUAGES).index(lang)

def lang_format(lang: str) -> str:
    """Format the language to show the language code and the language name.

    Args
    ----
        lang (str): The language.

    Returns
    -------
        str: The formatted language.
    """
    return f"{lang} ({MINECRAFT_LANGUAGES[lang]})"

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
    """Progress Bar Class

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
    pbar: DeltaGenerator
    task: str
    
    def __init__(self, iterable: Iterable, task: str):
        self.current = 0
        self.len = len(iterable)
        self.iterator = iter(iterable)
        self.pbar = st.progress(0)
        self.task = task
    
    def __iter__(self):
        return self

    def __next__(self):
        element = next(self.iterator)
        self.current += 1
        progress = self.current / self.len
        
        if self.task == "convert":
            pbar_text = Message("convert_quests", progress=progress*100).text
        elif self.task == "translate":
            pbar_text = Message("translate_quests", progress=progress*100).text
            
        self.pbar.progress(progress, text=pbar_text)
        return element
    
class DownloadButton:
    """Download Button Class
    
    Args
    ----
        data (BytesIO): The data to download.
        file_name (str): The name of the file to download.
    """
    def __init__(self, data: BytesIO, file_name: str) -> None:
        ste.download_button(
            label = MESSAGES["download_button"].format(file_name=file_name),
            data = data,
            file_name = file_name,
            mime = "application/octet-stream"
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
    localizer: QuestLocalizer
    src: str
    dest: str
    
    def __init__(self, localizer: QuestLocalizer):
        self.localizer = localizer
        self.src = localizer.src.lang
        self.dest = localizer.dest.lang
    
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
            DownloadButton(BytesIO(open(zip_dir, "rb").read()), zip_name)
    
    def download_json(self, template: bool = False) -> None:
        """Show the download button for the localized JSON files.

        Args
        ----
            template (bool, optional): If True, download the template JSON file. Defaults to False.
        """
        if template:
            DownloadButton(BytesIO(self.localizer.template_json.encode("utf-8")), "template_lang.json")
            with st.expander(Message("show_json").text):
                st.json(self.localizer.template_json)
            return
        
        if st.session_state.translate:
            DownloadButton(BytesIO(self.localizer.src_json.encode("utf-8")), f"{self.src}.json")
            DownloadButton(BytesIO(self.localizer.dest_json.encode("utf-8")), f"{self.dest}.json")
            with st.expander(Message("show_json").text):
                tab1, tab2 = st.tabs([f"{self.src}.json", f"{self.dest}.json"])
                tab1.json(self.localizer.src_json)
                tab2.json(self.localizer.dest_json)
        else:
            DownloadButton(BytesIO(self.localizer.src_json.encode("utf-8")), f"{self.src}.json")
            with st.expander(Message("show_json").text):
                st.json(self.localizer.src_json)