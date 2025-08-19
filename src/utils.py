import hashlib
import asyncio
from io import StringIO, BytesIO

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

import deepl
from langchain_google_genai import ChatGoogleGenerativeAI

from src.constants import MESSAGES

@st.cache_data(ttl=3600)
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

def schedule_task(key, coro):
    """Schedules an async task and stores it with a unique key."""
    if key not in st.session_state.tasks:
        st.session_state.tasks[key] = st.session_state.loop.create_task(coro)

def process_tasks():
    """Process pending tasks on the event loop."""
    pending = [task for task in st.session_state.tasks.values() if not task.done()]
    if pending:
        st.session_state.loop.run_until_complete(asyncio.gather(*pending))

def generate_task_key(*args):
    """Generate a unique hash-based key for a task."""
    return hashlib.sha256("-".join(map(str, args)).encode()).hexdigest()

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