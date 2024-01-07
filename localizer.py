from __future__ import annotations

import re
from io import BytesIO, StringIO
from googletrans import Translator


TITLE_REGEX = re.compile(r'(?<=\btitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
SUBTITLE_REGEX = re.compile(r'(?<=\bsubtitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
DESC_REGEX = re.compile(r'(?<=\bdescription: )\[[\s\S.]*?\]\s', flags=re.MULTILINE)
STRING_REGEX = re.compile(r'(?<=\")(?:(?=\\?)\\?.)*?(?=\")', flags=re.MULTILINE)

MODPACK_NAME = "atm9"

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
    
    def translate(self, target: QuestLang) -> dict:
        if target.lang != self.lang:
            for k, v in self.json.items():
                if v.startswith("[ ") and v.endswith(" ]"):
                    continue
                self.json[k] = self.translator.translate(v, dest=target).text
        return self.json
    
class QuestSNBT:
    snbt: str
    modpack: str
    chapter: str
    
    def __init__(self, data: str, modpack: str = "modpack", chapter: str = "chapter") -> None:
        self.snbt = data
        self.modpack = modpack
        self.chapter = chapter
    
    def convert(self, lang: QuestLang) -> tuple[str, dict]:
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
        self.quests = [QuestSNBT(StringIO(quest.getvalue().decode("utf-8")).read(), quest.name[:-5], self.modpack) for quest in quests]
    
    def convert_quests(self) -> None:
        for quest in self.quests:
            quest.convert(self.src_lang)
    
    def translate_quests(self) -> None:
        self.src_lang.translate(self.dest_lang)

if __name__ == "__main__":
    localizer = QuestLocalizer("en_us", "ko_kr", MODPACK_NAME)
    localizer.convert_quests(data=None)