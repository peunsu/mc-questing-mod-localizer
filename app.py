import os
import glob
import re
import json
from googletrans import Translator

TITLE_REGEX = re.compile(r'(?<=\btitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
SUBTITLE_REGEX = re.compile(r'(?<=\bsubtitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE)
DESC_REGEX = re.compile(r'(?<=\bdescription: )\[[\s\S.]*?\]\s', flags=re.MULTILINE)
IMAGE_REGEX = re.compile(r'{image:[0-9a-zA-Z]*:.*}', flags=re.MULTILINE)
COLOR_CODE_REGEX = re.compile(r'&[0-9A-FK-OR]', flags=re.IGNORECASE | re.MULTILINE)
STRING_REGEX = re.compile(r'(?<=\")(?:(?=\\?)\\?.)*?(?=\")', flags=re.MULTILINE)

QUEST_PATH = "./quests/"
OUTPUT_QUEST_PATH = "./output/quests/"
OUTPUT_LANG_PATH = "./output/lang/"

MODPACK_NAME = "atm9"

lang_dict = dict()

def replace_snbt(snbt: str, modpack: str, chapter: str) -> str:
    for key in ["description", "subtitle", "title"]:
        if key == "title":
            regex = TITLE_REGEX
        elif key == "subtitle":
            regex = SUBTITLE_REGEX
        elif key == "description":
            regex = DESC_REGEX
        
        for i, element in enumerate(regex.findall(snbt)):
            for j, el in enumerate(filter(lambda x: x, STRING_REGEX.findall(element))):
                snbt = snbt.replace(el, f"{{{modpack}.{chapter}.{key}.{i}.{j}}}", 1)
                lang_dict[f"{modpack}.{chapter}.{key}.{i}.{j}"] = el
                
    return snbt

os.makedirs(os.path.join(OUTPUT_QUEST_PATH, "chapters"), exist_ok=True)
os.makedirs(OUTPUT_LANG_PATH, exist_ok=True)

file_list = [os.path.join(QUEST_PATH, "chapter_groups.snbt"), *glob.glob(os.path.join(QUEST_PATH, "chapters/*.snbt"))]
for file_path in file_list:
    with open(file_path, "r", encoding="utf-8-sig") as f:
        snbt = f.read()
    snbt = replace_snbt(snbt, modpack=MODPACK_NAME, chapter=os.path.basename(file_path)[:-5])
    with open(file_path.replace(QUEST_PATH, os.path.join(OUTPUT_QUEST_PATH), 1), "w", encoding="utf-8-sig") as f:
        f.write(snbt)

json.dump(lang_dict, open(os.path.join(OUTPUT_LANG_PATH, "en_us.json"), "w"), indent=4, ensure_ascii=False)

translator = Translator()
results = translator.translate(list(lang_dict.values()), dest="ko")
ko_lang_dict = {k: v for k, v in zip(lang_dict.keys(), map(lambda x: x.text, results))}
json.dump(ko_lang_dict, open(os.path.join(OUTPUT_LANG_PATH, "ko_kr.json"), "w"), indent=4, ensure_ascii=False)