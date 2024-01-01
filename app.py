import os
import re
import json

TITLE_REGEX = re.compile(r'(?<=\btitle: )\"[\s\S.]*?\"', flags=re.MULTILINE)
SUBTITLE_REGEX = re.compile(r'(?<=\bsubtitle: )\"[\s\S.]*?\"', flags=re.MULTILINE)
DESC_REGEX = re.compile(r'(?<=\bdescription: )\[[\s\S.]*?\]\s', flags=re.MULTILINE)
IMAGE_REGEX = re.compile(r'{image:[0-9a-zA-Z]*:.*}', flags=re.MULTILINE)
COLOR_CODE_REGEX = re.compile(r'&[0-9A-FK-OR]', flags=re.IGNORECASE | re.MULTILINE)
STRING_REGEX = re.compile(r'(?<=\")(?:(?=\\?)\\?.)*?(?=\")', flags=re.MULTILINE)

QUEST_PATH = "/workspaces/ftbq-localization-tool/quests/"
OUTPUT_PATH = "/workspaces/ftbq-localization-tool/output/"

MODPACK_NAME = "atm9"

lang_en_us = dict()

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
                if el.startswith("["):
                    print(key)
                    print(element, end="\n\n")
                    print(el)
                snbt = snbt.replace(el, f"{{{modpack}.{chapter}.{key}.{i}.{j}}}", 1)
                lang_en_us[f"{modpack}.{chapter}.{key}.{i}.{j}"] = el
                
    return snbt

if not os.path.exists(os.path.join(OUTPUT_PATH, "chapters")):
    os.mkdir(os.path.join(OUTPUT_PATH, "chapters"))

with open(os.path.join(QUEST_PATH, "chapter_groups.snbt"), "r") as f:
    snbt = f.read()
snbt = replace_snbt(snbt, modpack=MODPACK_NAME, chapter="chapter_groups")
with open(os.path.join(OUTPUT_PATH, "chapter_groups.snbt"), "w") as f:
    f.write(snbt)

for filename in os.listdir(os.path.join(QUEST_PATH, "chapters")):
    with open(os.path.join(QUEST_PATH, "chapters", filename), "r") as f:
        snbt = f.read()
    snbt = replace_snbt(snbt, modpack=MODPACK_NAME, chapter=filename[:-5])
    with open(os.path.join(OUTPUT_PATH, "chapters", filename), "w") as f:
        f.write(snbt)

json.dump(lang_en_us, open(os.path.join(OUTPUT_PATH, "en_us.json"), "w"), indent=4)