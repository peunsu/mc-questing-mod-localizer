import deepl
import tempfile
import streamlit as st
import streamlit_ext as ste
import ftb_snbt_lib as slib

from abc import ABCMeta, abstractmethod
from io import BytesIO

from src.utils import *
from src.constants import *

from typing import Iterator, Iterable, TYPE_CHECKING
if TYPE_CHECKING:
    from src.localizer import Localizer, Locale
    from streamlit.delta_generator import DeltaGenerator

class Message:
    message: str
    stop: bool
    
    def __init__(self, key: str, stop: bool = False, **kwargs):
        self.message = MESSAGES[st.query_params.lang][key].format(**kwargs)
        self.stop = stop
    
    @property
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
    
    def toast(self) -> None:
        st.toast(body=self.message, icon="📝")
        if self.stop:
            st.stop()
    
    def subheader(self) -> None:
        st.subheader(self.message)
        if self.stop:
            st.stop()
    
    def title(self) -> None:
        st.title(self.message)
        if self.stop:
            st.stop()
            
class ProgressBar:
    task: str
    current: int
    len: int
    iterator: Iterator
    pbar: "DeltaGenerator"
    
    def __init__(self, iterable: Iterable, task: str) -> None:
        self.task = task
        self.current = 0
        self.len = len(iterable)
        self.iterator = iter(iterable)
        self.pbar = st.progress(0)
    
    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> tuple:
        element = next(self.iterator)
        self.current += 1
        progress = self.current / self.len
        
        if self.task == "convert":
            pbar_text = Message("convert_quests", current=self.current, len=self.len, progress=progress*100).text
        elif self.task == "translate":
            pbar_text = Message("translate_quests", current=self.current, len=self.len, progress=progress*100).text
            
        self.pbar.progress(progress, text=pbar_text)
        return element

class LanguageRadio:
    options: list = ["en_us", "ko_kr"]
    
    def show(self) -> None:
        lang = st.radio(
            label = "Site Language",
            options = self.options,
            format_func = lambda x: MINECRAFT_LANGUAGES[x]
        )
        st.query_params.lang = lang
        
class TranslatorRadio:
    options: list = ["Google", "DeepL"]
    
    def show(self) -> None:
        st.radio(
            label = "Translator Service",
            options = self.options,
            index = 0,
            key = "translator",
            on_change = reset_localize_button
        )

class DeepLKeyInput:
    def validate_key(self):
        if self.auth_key:
            try:
                self.usage = deepl.Translator(self.auth_key).get_usage()
            except:
                return False
        else:
            return False
        return True
    
    def show(self) -> None:
        self.auth_key = st.text_input(
            label = Message("deepl_key_label").text,
            help = Message("deepl_key_help").text,
            type = "password",
            on_change = reset_localize_button,
            disabled = st.session_state.translator != "DeepL"
        )
        if st.session_state.translator == "DeepL":
            if self.validate_key():
                usage = self.usage
                st.progress(usage.character.count / usage.character.limit, text=f"Characters used: {usage.character.count}/{usage.character.limit}")
            else:
                Message("deepl_key_error").warning()
        st.caption(Message("deepl_key_caption").text)
        
class HomeButton:
    def show(self) -> None:
        st.page_link(
            page = "home.py",
            label = Message("back_to_home").text,
            icon = "↩️"
        )

class FileUploader(metaclass=ABCMeta):
    files: list[BytesIO]
    _msg_key: str
    _header_key: str
    _ext: str
    _max_files: int
    
    def __init__(self) -> None:
        self.files = []
        
    def show(self) -> None:
        Message(self._header_key).subheader()
        Message(self._msg_key, max=self._max_files).info()
        self.files = st.file_uploader(
            label = "Upload file(s).",
            type = [self._ext],
            accept_multiple_files = True,
            help = Message("uploader_help").text,
            on_change = reset_localize_button,
            label_visibility="collapsed"
        )
        if not self.files:
            st.stop()
        elif len(self.files) > self._max_files:
            Message("uploader_exceed", max=self._max_files, stop=True).error()
        

class FTBLocaleUploader(FileUploader):
    _msg_key: str = "uploader_ftbq_lang"
    _header_key: str = "header_upload_lang"
    _ext: str = "json"
    _max_files: int = 1

class FTBRenewalLocaleUploader(FileUploader):
    _msg_key: str = "uploader_ftbq_renewal_lang"
    _header_key: str = "header_upload_lang"
    _ext: str = "snbt"
    _max_files: int = 1

class BQMLocaleUploader(FileUploader):
    _msg_key: str = "uploader_bqm_lang"
    _header_key: str = "header_upload_lang"
    _ext: str = "lang"
    _max_files: int = 1

class FTBQuestUploader(FileUploader):
    _msg_key: str = "uploader_ftbq_quest"
    _header_key: str = "header_upload_quest"
    _ext: str = "snbt"
    _max_files: int = MAX_FTB_QUEST_FILES

class BQMQuestUploader(FileUploader):
    _msg_key: str = "uploader_bqm_quest"
    _header_key: str = "header_upload_quest"
    _ext: str = "json"
    _max_files: int = 1
    
class ModpackInput:        
    def show(self) -> None:
        Message("header_modpack_name").subheader()
        self.text = st.text_input(
            label = Message("modpack_label").text,
            max_chars = MAX_MODPACK_NAME_LEN,
            help = Message("modpack_help").text,
            on_change = reset_localize_button
        )
        if not self.text:
            st.stop()

class SelectTaskRadio(metaclass=ABCMeta):
    _expander_check_key: str
    
    def format_func(self, task: int) -> str:
        if task == 0:
            return Message("select_task_convert").text
        elif task == 1:
            return Message("select_task_convert_no_translate").text
        elif task == 2:
            return Message("select_task_translate_only").text
        
    def update_state(self, task: int) -> None:
        if task == 0:
            st.session_state.translate = True
            st.session_state.translate_only = False
        elif task == 1:
            st.session_state.translate = False
            st.session_state.translate_only = False
        elif task == 2:
            st.session_state.translate = True
            st.session_state.translate_only = True
        
    def show(self) -> None:
        Message("header_select_task").subheader()
        task = st.radio(
            label = Message("select_task_label").text,
            options = [0, 1, 2],
            format_func = self.format_func,
            on_change = reset_localize_button,
            key = "task"
        )
        self.update_state(task)
        with st.expander(Message("expander_select_task_label").text):
            Message("expander_select_task").info()
        with st.expander(Message("expander_check_label").text):
            Message(self._expander_check_key).info()

class FTBSelectTaskRadio(SelectTaskRadio):
    _expander_check_key: str = "expander_check_ftbq"

class BQMSelectTaskRadio(SelectTaskRadio):
    _expander_check_key: str = "expander_check_bqm"

class LangExistRadio():
    _dir: str
    
    def show(self) -> None:
        Message("header_lang_check").subheader()
        st.radio(
            label = Message("lang_check_label", dir=self._dir).text,
            options = [True, False],
            format_func = lambda x: "Yes" if x else "No",
            index = 1,
            help = Message("lang_check_help").text,
            key = "lang_exist"
        )

class FTBLangExistRadio(LangExistRadio):
    _dir: str = "kubejs/assets/kubejs/lang"

class BQMLangExistRadio(LangExistRadio):
    _dir: str = "resources/betterquesting/lang"

class LangSelectBox(metaclass=ABCMeta):
    lang: str
    _label: str
    _help: str
    _disabled: bool
    
    def __init__(self) -> None:
        self.lang = None
        if st.session_state.translator == "Google":
            self.lang_list = list(MINECRAFT_TO_GOOGLE)
        elif st.session_state.translator == "DeepL":
            self.lang_list = list(MINECRAFT_TO_DEEPL)
    
    def __str__(self) -> None:
        return self.lang
    
    def lang_index(self, lang: str) -> int:
        return list(self.lang_list).index(lang)

    def lang_format(self, lang: str) -> str:
        return f"{lang} ({MINECRAFT_LANGUAGES[lang]})"
    
    def show(self) -> None:
        self.lang = st.selectbox(
            label = Message(self._label).text,
            options = self.lang_list,
            index = self.lang_index("en_us"),
            format_func = self.lang_format,
            help = Message(self._help).text,
            on_change = reset_localize_button,
            disabled = self._disabled
        )

class SrcLangSelectBox(LangSelectBox):
    _label: str = "src_label"
    _help: str = "src_help"
    
    def __init__(self):
        self._disabled = False
        super().__init__()

class DestLangSelectBox(LangSelectBox):
    _label: str = "dest_label"
    _help: str = "dest_help"

    def __init__(self):
        self._disabled = not st.session_state.translate
        super().__init__()

class LocalizeButton:    
    def show(self):
        st.button(
            label = Message("localize_label").text,
            help = Message("localize_help").text,
            on_click = localize_button,
            disabled = st.session_state.localize
        )
    
class LangLinkButton:
    def show(self) -> None:
        st.link_button(
            label = Message("lang_link_label").text,
            url = Message("lang_link_url").text,
            help = Message("lang_link_help").text
        )

class LocalizerManager:
    localizer: "Localizer"
    src: str
    dest: str
    _ext: str
    _dir: str
    _example: str
    
    def __init__(self, localizer: "Localizer") -> None:
        self.localizer = localizer
        self.src = localizer.src.lang
        self.dest = localizer.dest.lang
    
    def run(self) -> None:
        if not st.session_state.translate_only:
            self.convert()
        if st.session_state.translate:
            self.translate()
        
    def convert(self) -> None:
        try:
            self.localizer.convert()
        except Exception as e:
            Message("convert_error", stop=True, e=e).error()
        Message("convert_success").toast()
    
    def translate(self) -> None:
        if self.src == self.dest:
            Message("translate_same_lang", stop=True).error()
        try:
            self.localizer.translate()
        except Exception as e:
            Message("translate_error", stop=True, e=e).error()
        Message("translate_success").toast()
    
    def show_manual(self) -> None:
        st.divider()
        
        Message("header_apply_manual").subheader()
        if not st.session_state.translate_only:
            self.show_quest_manual()
        if st.session_state.translate:
            self.show_lang_manual()
        
        st.divider()
        
        Message("header_add_manual").subheader()
        self.show_custom_lang_manual()
    
    @abstractmethod
    def show_quest_manual(self) -> None:
        pass
    
    def show_lang_manual(self) -> None:
        if st.session_state.translate:
            Message("manual_translated_lang_1", src=self.src, dest=self.dest, ext=self._ext).send()
            self.show_download_button(self.locale_to_bytesio(self.localizer.src), f"{self.src}.{self._ext}")
            self.show_download_button(self.locale_to_bytesio(self.localizer.dest), f"{self.dest}.{self._ext}")
            Message("manual_translated_lang_2", src=self.src, dest=self.dest, ext=self._ext, dir=self._dir).send()
            Message("manual_translated_lang_3", dest=self.dest, ext=self._ext).send()
            Message("manual_lang_warning", ext=self._ext, example=self._example).warning()
        else:
            Message("manual_lang_1", src=self.src, ext=self._ext).send()
            self.show_download_button(self.locale_to_bytesio(self.localizer.src), f"{self.src}.{self._ext}")
            Message("manual_lang_2", src=self.src, ext=self._ext, dir=self._dir).send()
            Message("manual_lang_3").send()
    
    def show_custom_lang_manual(self) -> None:
        Message("manual_custom_lang_1", src=self.src, ext=self._ext).send()
        self.show_download_button(self.locale_to_bytesio(self.localizer.src), f"{self.src}.{self._ext}")
        self.show_download_button(self.locale_to_bytesio(self.localizer.template), f"template.{self._ext}")
        Message("manual_custom_lang_2", ext=self._ext).send()
        LangLinkButton().show()
        Message("manual_custom_lang_3", src=self.src, ext=self._ext).send()
        Message("manual_custom_warning", src=self.src, ext=self._ext, dir=self._dir).warning()
        Message("manual_custom_lang_4", src=self.src, ext=self._ext, dir=self._dir).send()
        Message("manual_custom_lang_5").send()
    
    @staticmethod
    def show_download_button(data: BytesIO, filename: str) -> None:
        ste.download_button(
            label = Message("download_button", filename=filename).text,
            data = data,
            file_name = filename,
            mime = "application/octet-stream"
        )
        
    @staticmethod
    @abstractmethod
    def locale_to_bytesio(locale: "Locale") -> BytesIO:
        pass

class FTBLocalizerManager(LocalizerManager):
    _ext: str = "json"
    _dir: str = "kubejs/assets/kubejs/lang"
    _example: str = "modpack.chapter.quests0.title"
    
    def show_quest_manual(self) -> None:
        Message("manual_ftbq_1").send()
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_name = "quests.zip"
            zip_dir = self.localizer.compress_quests(tmp_dir, zip_name)
            self.show_download_button(BytesIO(open(zip_dir, "rb").read()), zip_name)
        Message("manual_ftbq_2").send()
    
    @staticmethod
    def locale_to_bytesio(locale: "Locale") -> BytesIO:
        return BytesIO(json.dumps(locale.data, indent=4, ensure_ascii=False).encode("utf-8"))

class FTBRenewalLocalizerManager(LocalizerManager):
    _ext: str = "snbt"
    _dir: str = "config/ftbquests/quests/lang"
    _example: str = "chapter.01B56BD678E7745B.title"
    
    def show_quest_manual(self) -> None:
        return

    @staticmethod
    def locale_to_bytesio(locale: "Locale") -> BytesIO:
        return BytesIO(slib.dumps(locale.data).encode("utf-8"))

class BQMLocalizerManager(LocalizerManager):
    _ext: str = "lang"
    _dir: str = "resources/betterquesting/lang"
    _example: str = "modpack.quest0.name"
    
    def show_quest_manual(self) -> None:
        Message("manual_bqm_1").send()
        self.show_download_button(BytesIO(json.dumps(self.localizer.quests[0].data, indent=4, ensure_ascii=False).encode("utf-8")), "DefaultQuests.json")
        Message("manual_bqm_2").send()
        
    @staticmethod
    def locale_to_bytesio(locale: "Locale") -> BytesIO:
        return BytesIO(locale.dump_to_lang().encode("utf-8"))