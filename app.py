import re
import json
import shutil

from pathlib import Path
from googletrans import Translator

TITLE_REGEX = re.compile(r'(?<=\btitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
SUBTITLE_REGEX = re.compile(r'(?<=\bsubtitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
DESC_REGEX = re.compile(r'(?<=\bdescription: )\[[\s\S.]*?\]\s', flags=re.MULTILINE)
IMAGE_REGEX = re.compile(r'{image:[0-9a-zA-Z]*:.*}', flags=re.MULTILINE)
STRING_REGEX = re.compile(r'(?<=\")(?:(?=\\?)\\?.)*?(?=\")', flags=re.MULTILINE)

QUEST_PATH = Path("./quests")
OUTPUT_PATH = Path("./output")
OUTPUT_QUEST_PATH = OUTPUT_PATH / "quests"
OUTPUT_LANG_PATH = OUTPUT_PATH / "lang"

MODPACK_NAME = "atm9"

lang_dict = dict()

def convert_snbt(snbt: str, modpack: str, chapter: str) -> str:
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
        
        for i, element in enumerate(regex.findall(snbt)):
            for j, el in enumerate(filter(filter_string, STRING_REGEX.findall(element))):
                snbt = snbt.replace(f'"{el}"', f'"{{{modpack}.{chapter}.{key}.{i}.{j}}}"')
                lang_dict[f"{modpack}.{chapter}.{key}.{i}.{j}"] = el
    return snbt

def translate_lang(lang_dict: dict, dest: str) -> dict:
    translator = Translator()
    for k, v in lang_dict.items():
        lang_dict[k] = translator.translate(v, dest=dest).text
    return lang_dict

def save_lang(lang_dict: dict, lang: str="en_us") -> None:
    OUTPUT_LANG_PATH.mkdir(parents=True, exist_ok=True)
    json.dump(lang_dict, open(OUTPUT_LANG_PATH/f"{lang}.json", "w", encoding="utf-8-sig"), indent=4, ensure_ascii=False)

def copy_quests() -> None:
    try:
        shutil.copytree(QUEST_PATH, OUTPUT_QUEST_PATH)
    except FileExistsError:
        check = input("output/quests already exists. Do you want to delete it? (y/n): ")
        if check == "y":
            shutil.rmtree(OUTPUT_QUEST_PATH)
            shutil.copytree(QUEST_PATH, OUTPUT_QUEST_PATH)
        else:
            print("Aborted.")
            exit(1)

def convert_quests() -> None:
    for file_path in Path(OUTPUT_QUEST_PATH).glob('**/*.snbt'):
        with open(file_path, "r", encoding="utf-8-sig") as f:
            snbt = f.read()
        chapter = file_path.stem.replace(" ", "_")
        snbt = convert_snbt(snbt, modpack=MODPACK_NAME, chapter=chapter)
        with open(file_path, "w", encoding="utf-8-sig") as f:
            f.write(snbt)

if __name__ == "__main__":
    copy_quests()
    convert_quests()
    save_lang(lang_dict, "en_us")

    #ko_lang_dict = translate_lang(lang_dict, "ko")
    #save_lang(ko_lang_dict, "ko_kr")