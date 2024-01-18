from __future__ import annotations

import os
import json
import zipfile

from time import sleep
from io import BytesIO, StringIO
from googletrans import Translator
from streamlit.delta_generator import DeltaGenerator
from constants import MINECRAFT_TO_GOOGLE, REGEX, MAX_RETRY

def progress_bar(iterable, pbar: DeltaGenerator, pbar_text: str) -> None:    
    idx = 0
    for element in iterable:
        idx += 1
        progress = idx / len(iterable)
        pbar.progress(progress, text=pbar_text.format(progress=progress*100))
        yield element

class QuestLang:
    lang: str
    json: dict
    translator: Translator
    
    def __init__(self, lang: str = "en_us"):
        self.lang = lang
        self.json = dict()
        self.translator = Translator()
    
    def __repr__(self) -> str:
        return f"QuestLang(lang={self.lang}, json={self.json})"
    
    def __str__(self) -> str:
        return self.lang
    
    def __eq__(self, other: QuestLang) -> bool:
        return self.lang == other.lang
    
    def __ne__(self, other: QuestLang) -> bool:
        return self.lang != other.lang
    
    def is_empty(self) -> bool:
        return not self.json

    def copy_from(self, other: QuestLang) -> None:
        self.json = other.json.copy()
    
    def update(self, key: str, value: str) -> None:
        self.json[key] = value
    
    def translate(self, target: QuestLang, pbar: DeltaGenerator, pbar_text: str) -> None:
        if target.is_empty():
            target.copy_from(self)
        if target != self:
            for key, text in progress_bar(self.json.items(), pbar, pbar_text):
                if text.startswith("[ ") and text.endswith(" ]"):
                    continue
                target.update(key=key, value=self._translate(text, target))
    
    def _translate(self, text: str, target: QuestLang) -> str:
        retry_count = 0
        while True:
            try:
                return self.translator.translate(text, dest=MINECRAFT_TO_GOOGLE[target.lang]).text
            except Exception as e:
                retry_count += 1
                if retry_count == MAX_RETRY:
                    raise e
                sleep(3)
    
    
class QuestSNBT:
    snbt: str
    modpack: str
    chapter: str
    
    def __init__(self, data: str, modpack: str, chapter: str) -> None:
        self.snbt = data
        self.modpack = modpack
        self.chapter = chapter
    
    def __repr__(self) -> str:
        return f"QuestSNBT(snbt={self.snbt}, modpack={self.modpack}, chapter={self.chapter})"

    def __str__(self) -> str:
        return self.chapter
    
    def convert(self, lang: QuestLang) -> None:
        for key in ["description", "subtitle", "title"]:
            self._convert(lang, key)
    
    def _filter(self, string: str) -> bool:
        if not string:
            return False
        if string[0] == "{" and string[-1] == "}":
            return False
        return True
    
    def _replace_snbt(self, old: str, new: str) -> None:
        self.snbt = self.snbt.replace(old, new)
    
    def _convert(self, lang: QuestLang, key: str) -> None:        
        regex = REGEX[key]
        for i, element in enumerate(regex.findall(self.snbt)):
            for j, el in enumerate(filter(self._filter, REGEX["string"].findall(element))):
                self._replace_snbt(f'"{el}"', f'"{{{self.modpack}.{self.chapter}.{key}.{i}.{j}}}"')
                lang.update(key=f"{self.modpack}.{self.chapter}.{key}.{i}.{j}", value=el)

class QuestLocalizer:
    src_lang: QuestLang
    dest_lang: QuestLang
    modpack: str
    quests: list[QuestSNBT]
    
    def __init__(self, quests: list[BytesIO], src: str, dest: str, modpack: str) -> None:
        self.src_lang = QuestLang(src)
        self.dest_lang = QuestLang(dest)
        self.modpack = REGEX["strip"].sub("", modpack.lower().replace(" ", "_"))
        self.quests = [QuestSNBT(
            data = StringIO(quest.getvalue().decode("utf-8")).read(),
            modpack = self.modpack,
            chapter = os.path.splitext(quest.name)[0]
            ) for quest in quests]
    
    def __repr__(self) -> str:
        return f"QuestLocalizer(src_lang={self.src_lang}, dest_lang={self.dest_lang}, modpack={self.modpack}, quests={self.quests})"

    def __str__(self) -> str:
        return self.modpack
    
    def convert_quests(self, pbar: DeltaGenerator, pbar_text: str) -> None:
        for quest in progress_bar(self.quests, pbar, pbar_text):
            quest.convert(self.src_lang)
    
    def translate_quests(self, pbar: DeltaGenerator, pbar_text: str) -> None:
        self.src_lang.translate(self.dest_lang, pbar, pbar_text)
    
    def compress_quests(self, dir: str) -> str:
        zip_dir = os.path.join(dir, 'localized_snbt.zip')
        with zipfile.ZipFile(zip_dir, 'w') as zip_obj:
            for quest in self.quests:
                zip_obj.writestr(f"{quest.chapter}.snbt", quest.snbt)
        return zip_dir
    
    @property
    def src_json(self) -> str:
        return json.dumps(self.src_lang.json, indent=4, ensure_ascii=False)

    @property
    def dest_json(self) -> str:
        return json.dumps(self.dest_lang.json, indent=4, ensure_ascii=False)

    @property
    def template_json(self) -> str:
        temp_json = self.src_lang.json.copy()
        for k in temp_json.keys():
            temp_json[k] = ""
        return json.dumps(temp_json, indent=4, ensure_ascii=False)