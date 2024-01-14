from __future__ import annotations

import os
import json
import zipfile

from time import sleep
from io import BytesIO, StringIO
from googletrans import Translator
from streamlit.delta_generator import DeltaGenerator
from constants import MINECRAFT_TO_GOOGLE, TITLE_REGEX, SUBTITLE_REGEX, DESC_REGEX, STRING_REGEX, MAX_RETRY

class QuestLang:
    lang: str
    json: dict
    translator: Translator
    
    def __init__(self, lang: str = "en_us"):
        self.lang = lang
        self.json = dict()
        self.translator = Translator()
    
    def update(self, key: str, value: str) -> None:
        self.json[key] = value
    
    def translate(self, target: QuestLang, pbar: DeltaGenerator, pbar_text: str) -> None:
        if not target.json:
            target.json = self.json.copy()
        if target.lang != self.lang:
            for idx, (k, v) in enumerate(self.json.items()):
                if v.startswith("[ ") and v.endswith(" ]"):
                    continue
                retry_count = 0
                while True:
                    try:
                        target.json[k] = self.translator.translate(v, dest=MINECRAFT_TO_GOOGLE[target.lang]).text
                        break
                    except Exception as e:
                        retry_count += 1
                        if retry_count == MAX_RETRY:
                            raise e
                        sleep(5)
                progress = (idx + 1) / len(self.json)
                pbar.progress(progress, text=pbar_text.format(progress=f"{progress * 100:.2f}%"))
        pbar.progress(1.0, text="Successfully translated!")
    
class QuestSNBT:
    snbt: str
    modpack: str
    chapter: str
    
    def __init__(self, data: str, modpack: str = "modpack", chapter: str = "chapter") -> None:
        self.snbt = data
        self.modpack = modpack
        self.chapter = chapter
    
    def convert(self, lang: QuestLang) -> None:
        def filter_string(string: str) -> bool:
            if not string:
                return False
            if string[0] == "{" and string[-1] == "}":
                return False
            return True
        
        for key in ["description", "subtitle", "title"]:
            if key == "title":
                regex = TITLE_REGEX
            elif key == "subtitle":
                regex = SUBTITLE_REGEX
            elif key == "description":
                regex = DESC_REGEX
            
            for i, element in enumerate(regex.findall(self.snbt)):
                for j, el in enumerate(filter(filter_string, STRING_REGEX.findall(element))):
                    self.snbt = self.snbt.replace(f'"{el}"', f'"{{{self.modpack}.{self.chapter}.{key}.{i}.{j}}}"')
                    lang.update(f"{self.modpack}.{self.chapter}.{key}.{i}.{j}", el)

class QuestLocalizer:
    src_lang: QuestLang
    dest_lang: QuestLang
    modpack: str
    quests: list[QuestSNBT]
    
    def __init__(self, quests: list[BytesIO], src: str, dest: str, modpack: str = "modpack") -> None:
        self.src_lang = QuestLang(src)
        self.dest_lang = QuestLang(dest)
        self.modpack = modpack
        self.quests = [QuestSNBT(StringIO(quest.getvalue().decode("utf-8")).read(), self.modpack, quest.name[:-5]) for quest in quests]
    
    def convert_quests(self, pbar: DeltaGenerator, pbar_text: str) -> None:
        for idx, quest in enumerate(self.quests):
            quest.convert(self.src_lang)
            progress = (idx + 1) / len(self.quests)
            pbar.progress(progress, text=pbar_text.format(progress=f"{progress * 100:.2f}%"))
        pbar.progress(1.0, text="Successfully converted!")
    
    def translate_quests(self, pbar: DeltaGenerator, pbar_text: str) -> None:
        self.src_lang.translate(self.dest_lang, pbar, pbar_text)
    
    def compress_quests(self, dir: str) -> str:
        zip_dir = os.path.join(dir, 'localized_snbt.zip')
        with zipfile.ZipFile(zip_dir, 'w') as zip_obj:
            for quest in self.quests:
                zip_obj.writestr(f"{quest.chapter}.snbt", quest.snbt)
        return zip_dir
    
    def get_src_json(self) -> str:
        return json.dumps(self.src_lang.json, indent=4, ensure_ascii=False)

    def get_dest_json(self) -> str:
        return json.dumps(self.dest_lang.json, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    localizer = QuestLocalizer(None, "en_us", "ko_kr", "atm9")
    localizer.convert_quests()
    localizer.translate_quests()