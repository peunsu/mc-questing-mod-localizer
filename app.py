import re
import json
import shutil

from pathlib import Path
from googletrans import Translator

TITLE_REGEX = re.compile(r'(?<=\btitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
SUBTITLE_REGEX = re.compile(r'(?<=\bsubtitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
DESC_REGEX = re.compile(r'(?<=\bdescription: )\[[\s\S.]*?\]\s', flags=re.MULTILINE)
#IMAGE_REGEX = re.compile(r'{image:[0-9a-zA-Z]*:.*}', flags=re.MULTILINE)
STRING_REGEX = re.compile(r'(?<=\")(?:(?=\\?)\\?.)*?(?=\")', flags=re.MULTILINE)

QUEST_PATH = Path("./quests")
OUTPUT_PATH = Path("./output")

MODPACK_NAME = "atm9"

class LocalizerLang:
    fp: Path
    lang: dict
    target_lang: str
    translator: Translator
    
    def __init__(self, fp: str | Path, target_lang: str = None):
        if isinstance(fp, str):
            fp = Path(fp)
            
        self.fp = fp
        self.translator = Translator()
        self.target_lang = target_lang
        
        try:
            self.lang = json.load(open(self.fp, "r", encoding="utf-8-sig"))
        except FileNotFoundError:
            self.lang = dict()
        
        if self.target_lang is None:
            self.target_lang = self.fp.stem
    
    def update(self, key: str, value: str) -> None:
        self.lang[key] = value
    
    def translate(self) -> None:
        if self.target_lang == self.fp.stem:
            raise ValueError("target_lang is same as source_lang")
        
        for k, v in self.lang.items():
            if v.startswith("[ ") and v.endswith(" ]"):
                continue
            self.lang[k] = self.translator.translate(v, dest=self.target_lang).text
    
    def save(self) -> None:
        self.fp.parent.mkdir(parents=True, exist_ok=True)
        json.dump(self.lang, open(self.fp.parent/f"{self.target_lang}.json", "w", encoding="utf-8-sig"), indent=4, ensure_ascii=False)
    
class LocalizerSNBT:
    fp: Path
    snbt: str
    lang: LocalizerLang
    modpack: str
    chapter: str
    
    def __init__(self, fp: str | Path, lang: LocalizerLang, modpack: str = "modpack") -> None:
        if isinstance(fp, str):
            fp = Path(fp)
            
        self.fp = fp
        self.lang = lang
        self.modpack = modpack
        self.chapter = self.fp.stem.replace(" ", "_")
        
        with open(self.fp, "r", encoding="utf-8-sig") as f:
            self.snbt = f.read()
    
    def convert(self) -> None:
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
                    self.lang.update(f"{self.modpack}.{self.chapter}.{key}.{i}.{j}", el)
    
    def save(self) -> None:
        with open(self.fp, "w", encoding="utf-8-sig") as f:
            f.write(self.snbt)
        self.lang.save()

class Localizer:
    src_path: Path
    dest_path: Path
    quest_path: Path
    lang_path: Path
    modpack: str
    lang: LocalizerLang
    
    def __init__(self, src_path: str | Path, dest_path: str | Path, modpack: str = "modpack") -> None:
        if isinstance(src_path, str):
            src_path = Path(src_path)
        if isinstance(dest_path, str):
            dest_path = Path(dest_path)
            
        self.src_path = src_path
        self.dest_path = dest_path
        self.quest_path = self.dest_path / "quests"
        self.lang_path = self.dest_path / "lang"
        self.modpack = modpack
        self.lang = LocalizerLang(self.lang_path/"en_us.json")
    
    def copy_quests(self) -> None:
        try:
            shutil.copytree(self.src_path, self.quest_path)
        except FileExistsError:
            check = input(f"{self.quest_path} already exists. Do you want to delete it? (y/n): ")
            if check == "y":
                shutil.rmtree(self.quest_path)
                shutil.copytree(self.src_path, self.quest_path)
            else:
                print("Aborted.")
                raise KeyboardInterrupt
    
    def convert_quests(self) -> None:
        for file_path in self.dest_path.glob('**/*.snbt'):
            snbt = LocalizerSNBT(file_path, self.lang, self.modpack)
            snbt.convert()
            snbt.save()

if __name__ == "__main__":
    localizer = Localizer(QUEST_PATH, OUTPUT_PATH, MODPACK_NAME)
    localizer.copy_quests()
    localizer.convert_quests()