from io import StringIO, BytesIO
from tqdm.asyncio import tqdm_asyncio

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

import deepl
from langchain_google_genai import ChatGoogleGenerativeAI

from src.constants import MESSAGES

def read_file(file: BytesIO) -> str:
    try:
        return StringIO(file.getvalue().decode('utf-8')).read()
    except UnicodeDecodeError:
        return StringIO(file.getvalue().decode('ISO-8859-1')).read()

def write_file(data: str) -> BytesIO:
    return BytesIO(data.encode('utf-8'))

def get_session_id() -> str:
    return get_script_run_ctx().session_id

@st.cache_data(ttl=60)
def check_deepl_key(auth_key: str) -> bool:
    try:
        deepl_client = deepl.DeepLClient(auth_key)
        usage = deepl_client.get_usage()
        return usage.character.count < usage.character.limit
    except:
        return False

@st.cache_data(ttl=360)
def check_gemini_key(auth_key: str) -> bool:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=auth_key,
            temperature=0
        )
        llm.invoke("ping")
        return True
    except:
        return False

class Message:
    message: str
    stop: bool
    
    def __init__(self, key: str, stop: bool = False, st_container = st, **kwargs):
        self.message = MESSAGES[st.session_state.language][key].format(**kwargs)
        self.stop = stop
        self.st_container = st_container

    @property
    def text(self) -> str:
        return self.message
    
    def send(self) -> None:
        self.st_container.write(self.message)
        if self.stop:
            self.st_container.stop()

    def info(self) -> None:
        self.st_container.info(self.message)
        if self.stop:
            self.st_container.stop()

    def warning(self) -> None:
        self.st_container.warning(self.message)
        if self.stop:
            self.st_container.stop()

    def error(self) -> None:
        self.st_container.error(self.message)
        if self.stop:
            self.st_container.stop()

    def caption(self) -> None:
        self.st_container.caption(self.message)
        if self.stop:
            self.st_container.stop()

    def toast(self) -> None:
        self.st_container.toast(body=self.message)
        if self.stop:
            self.st_container.stop()

    def subheader(self) -> None:
        self.st_container.subheader(self.message)
        if self.stop:
            self.st_container.stop()

    def title(self) -> None:
        self.st_container.title(self.message)
        if self.stop:
            self.st_container.stop()

class stqdm_asyncio(tqdm_asyncio):
    '''
    Copyright 2023 Wirg

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    '''
    def __init__(
        self,
        iterable=None,
        desc=None,
        total=None,
        leave=True,
        file=None,
        ncols=None,
        mininterval=0.1,
        maxinterval=10.0,
        miniters=None,
        ascii=None,
        disable=False,
        unit="it",
        unit_scale=False,
        dynamic_ncols=False,
        smoothing=0.3,
        bar_format=None,
        initial=0,
        position=None,
        postfix=None,
        unit_divisor=1000,
        write_bytes=None,
        lock_args=None,
        nrows=None,
        colour=None,
        gui=False,
        st_container=None,
        backend=False,
        frontend=True,
        **kwargs,
    ):  
        if st_container is None:
            st_container = st
        self._backend = backend
        self._frontend = frontend
        self.st_container = st_container
        self._st_progress_bar = None
        self._st_text = None
        super().__init__(
            iterable=iterable,
            desc=desc,
            total=total,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=mininterval,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            disable=disable,
            unit=unit,
            unit_scale=unit_scale,
            dynamic_ncols=dynamic_ncols,
            smoothing=smoothing,
            bar_format=bar_format,
            initial=initial,
            position=position,
            postfix=postfix,
            unit_divisor=unit_divisor,
            write_bytes=write_bytes,
            lock_args=lock_args,
            nrows=nrows,
            colour=colour,
            gui=gui,
            **kwargs,
        )

    @property
    def st_progress_bar(self) -> st.progress:
        if self._st_progress_bar is None:
            self._st_progress_bar = self.st_container.empty()
        return self._st_progress_bar

    @property
    def st_text(self) -> st.empty:
        if self._st_text is None:
            self._st_text = self.st_container.empty()
        return self._st_text

    def st_display(self, n, total, **kwargs): 
        if total is not None and total > 0:
            self.st_text.write(self.format_meter(n, total, **{**kwargs, "ncols": 0}))
            self.st_progress_bar.progress(n / total)
        if total is None:
            self.st_text.write(self.format_meter(n, total, **{**kwargs, "ncols": 0}))

    def display(self, msg=None, pos=None):
        if self._backend:
            super().display(msg, pos)
        if self._frontend:
            self.st_display(**self.format_dict)
        return True

    def st_clear(self):
        if self._st_text is not None:
            self._st_text.empty()
            self._st_text = None
        if self._st_progress_bar is not None:
            self._st_progress_bar.empty()
            self._st_progress_bar = None

    def close(self):
        super().close()
        self.st_clear()
