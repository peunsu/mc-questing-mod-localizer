from __future__ import annotations

import os
import json
import zipfile

from time import sleep
from io import BytesIO, StringIO
from googletrans import Translator
from utils import ProgressBar
from constants import MINECRAFT_TO_GOOGLE, REGEX, MAX_RETRY

class QuestLang:
    """FTB Quests Language Class
    
    Args
    ----
        lang (str): The language of the quests.
    
    Attributes
    ----------
        lang (str): The language of the quests.
        json (dict): The dictionary containing the text.
        translator (googletrans.Translator): The translator.
    """
    lang: str
    json: dict
    translator: Translator
    
    def __init__(self, lang: str):
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
        """Check if the language dictionary is empty.

        Returns
        -------
            bool: True if the language dictionary is empty, False otherwise.
        """
        return not self.json

    def copy_from(self, other: QuestLang) -> None:
        """Copy the language dictionary from another QuestLang object.

        Args
        ----
            other (QuestLang): The QuestLang object to copy from.
        """
        self.json = other.json.copy()
    
    def update(self, key: str, value: str) -> None:
        """Update the language dictionary.

        Args
        ----
            key (str): The key of the dictionary to update.
            value (str): The value of the dictionary to update.
        """
        self.json[key] = value
    
    def translate(self, target: QuestLang) -> None:
        """Translate the language dictionary.

        Args
        ----
            target (QuestLang): The QuestLang object to translate into.
        """
        if target.is_empty():
            target.copy_from(self)
        if target != self:
            for key, text in ProgressBar(self.json.items(), task="translate"):
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
    """FTB Quests SNBT Class
    
    Args
    ----
        data (str): The SNBT data.
        modpack (str): The modpack name.
        chapter (str): The chapter name.
    
    Attributes
    ----------
        snbt (str): The SNBT data.
        modpack (str): The modpack name.
        chapter (str): The chapter name.
    """
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
        """Convert the SNBT data.

        Args
        ----
            lang (QuestLang): The QuestLang object to save the converted text.
        """
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
    """FTB Quests Localizer Class

    Args
    ----
        quests (list[BytesIO]): The list of BytesIO objects containing the quests.
        src (str): The source language.
        dest (str): The destination language.
        modpack (str): The modpack name.
    
    Attributes
    ----------
        src (QuestLang): The QuestLang object of the source language.
        dest (QuestLang): The QuestLang object of the destination language.
        modpack (str): The modpack name.
        quests (list[QuestSNBT]): The list of QuestSNBT objects.
    """
    src: QuestLang
    dest: QuestLang
    modpack: str
    quests: list[QuestSNBT]
    
    def __init__(self, quests: list[BytesIO], src: str, dest: str, modpack: str) -> None:
        self.src = QuestLang(src)
        self.dest = QuestLang(dest)
        self.modpack = REGEX["strip"].sub("", modpack.lower().replace(" ", "_"))
        self.quests = [QuestSNBT(
            data = StringIO(quest.getvalue().decode("utf-8")).read(),
            modpack = self.modpack,
            chapter = os.path.splitext(quest.name)[0]
            ) for quest in quests]
    
    def __repr__(self) -> str:
        return f"QuestLocalizer(src={self.src}, dest={self.dest}, modpack={self.modpack}, quests={self.quests})"

    def __str__(self) -> str:
        return self.modpack
    
    def convert_quests(self) -> None:
        """Convert the quests.
        """
        for quest in ProgressBar(self.quests, task="convert"):
            quest.convert(self.src)
    
    def translate_quests(self) -> None:
        """Translate the quests.
        """
        self.src.translate(self.dest)
    
    def compress_quests(self, dir: str, file_name: str = "localized_snbt.zip") -> str:
        """Compress the quests into a zip file.

        Args
        ----
            dir (str): The directory to save the zip file.
            file_name (str, optional): The name of the zip file.

        Returns
        -------
            str: The path of the zip file.
        """
        zip_dir = os.path.join(dir, file_name)
        with zipfile.ZipFile(zip_dir, 'w') as zip_obj:
            for quest in self.quests:
                zip_obj.writestr(f"{quest.chapter}.snbt", quest.snbt)
        return zip_dir
    
    @property
    def src_json(self) -> str:
        """Get the JSON string of the source language.

        Returns
        -------
            str: The JSON string of the source language.
        """
        return json.dumps(self.src.json, indent=4, ensure_ascii=False)

    @property
    def dest_json(self) -> str:
        """Get the JSON string of the destination language.

        Returns
        -------
            str: The JSON string of the destination language.
        """
        return json.dumps(self.dest.json, indent=4, ensure_ascii=False)

    @property
    def template_json(self) -> str:
        """Get the JSON string of the template language.

        Returns
        -------
            str: The JSON string of the template language.
        """
        temp = QuestLang("template")
        temp.copy_from(self.src)
        for k in temp.json.keys():
            temp.update(key=k, value="")
        return json.dumps(temp.json, indent=4, ensure_ascii=False)