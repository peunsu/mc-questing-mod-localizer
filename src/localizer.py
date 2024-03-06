from __future__ import annotations

import os
import json
import zipfile

from abc import ABCMeta, abstractmethod
from overrides import overrides, final
from io import BytesIO, StringIO
from time import sleep
from googletrans import Translator
from .components import ProgressBar
from .constants import MINECRAFT_TO_GOOGLE, REGEX, MAX_RETRY

__all__ = [
    "QuestLang",
    "QuestData",
    "FTBQuestData",
    "BQMQuestData",
    "QuestLocalizer",
    "FTBQuestLocalizer",
    "BQMQuestLocalizer"
]

class QuestLang:
    """Quest Language Class
    
    Args
    ----
        lang (str): The language of the quests.
        json (dict, optional): The dictionary containing the text.
    
    Attributes
    ----------
        lang (str): The language of the quests.
        json (dict): The dictionary containing the text.
        translator (googletrans.Translator): The translator.
    """
    lang: str
    json: dict
    translator: Translator
    
    def __init__(self, lang: str, json: dict = None) -> None:
        self.lang = lang
        self.json = dict() if json is None else json.copy()
        self.translator = Translator()
    
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
    
    def convert_to_lang(self, allow_blank: bool = False) -> str:
        """Convert the language dictionary to a LANG file format.

        Returns:
            str: The converted LANG file.
        """
        lang = "#PARSE_ESCAPES\n\n"
        for key, value in self.json.items():
            if not allow_blank and not value:
                continue
            value = value.replace("\n", "\\n")
            lang += f"{key}={value}\n"
        return lang
    
    def load_from_lang(self, lang: str) -> None:
        """Load the language dictionary from a LANG file.

        Args
        ----
            lang (str): The LANG file.
        """
        self.json = dict()
        for line in lang.splitlines():
            if line.startswith("#") or not line:
                continue
            key, value = REGEX["lang"].match(line).groups()
            self.update(key=key, value=value.replace("\\n", "\n"))
    
    def clear_values(self) -> None:
        """Clear the values of the language dictionary.
        """
        for key in self.json.keys():
            self.update(key=key, value="")
    
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
            target.json = self.json.copy()
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

class QuestData(metaclass=ABCMeta):
    """Quest Data Class (Abstract)
    
    Args
    ----
        data (str): The quest data.
        modpack (str): The modpack name.
        chapter (str, optional): The chapter name.
    
    Attributes
    ----------
        data (str): The quest data.
        modpack (str): The modpack name.
        chapter (str): The chapter name.
    """
    data: str
    modpack: str
    chapter: str
    
    @abstractmethod
    def __init__(self, data: str, modpack: str, chapter: str = None) -> None:
        pass
    
    @abstractmethod
    def convert(self, lang: QuestLang) -> None:
        """Convert the quest data.
        """
        pass
    
class FTBQuestData(QuestData):
    """FTB Quests Data Class
    
    Args
    ----
        data (str): The quest data.
        modpack (str): The modpack name.
        chapter (str): The chapter name.
    
    Attributes
    ----------
        data (str): The quest data.
        modpack (str): The modpack name.
        chapter (str): The chapter name.
    """
    data: str
    modpack: str
    chapter: str
    
    @overrides
    def __init__(self, data: str, modpack: str, chapter: str) -> None:
        self.data = data
        self.modpack = modpack
        self.chapter = chapter
    
    @overrides
    def convert(self, lang: QuestLang) -> None:
        """Convert the quest data.

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
    
    def _replace_data(self, old: str, new: str) -> None:
        self.data = self.data.replace(old, new)
    
    def _convert(self, lang: QuestLang, key: str) -> None:        
        regex = REGEX[key]
        for i, element in enumerate(regex.findall(self.data)):
            for j, el in enumerate(filter(self._filter, REGEX["string"].findall(element))):
                self._replace_data(f'"{el}"', f'"{{{self.modpack}.{self.chapter}.{key}.{i}.{j}}}"')
                lang.update(key=f"{self.modpack}.{self.chapter}.{key}.{i}.{j}", value=el)

class BQMQuestData(QuestData):
    """BQM Quest Data Class
    
    Args
    ----
        data (str): The quest data.
        modpack (str): The modpack name.
        chapter (str, optional): The chapter name.
    
    Attributes
    ----------
        data (str): The quest data.
        modpack (str): The modpack name.
        chapter (str): The chapter name.
    """
    data: str
    modpack: str
    chapter: str
    
    @overrides
    def __init__(self, data: str, modpack: str, chapter: str = None) -> None:
        self.data = data
        self.modpack = modpack
        self.chapter = chapter
    
    @overrides
    def convert(self, lang: QuestLang) -> None:
        """Convert the quest data.

        Args
        ----
            lang (QuestLang): The QuestLang object to save the converted text.
        """
        if self.data.get("questDatabase:9"):
            self._convert_quest_v2(lang, self.data["questDatabase:9"])
            self._convert_line_v2(lang, self.data["questLines:9"])
        else:
            self._convert_quest_v1(lang, self.data["questDatabase"])
            self._convert_line_v1(lang, self.data["questLines"])
    
    def _convert_quest_v1(self, lang: QuestLang, quests: dict) -> None:
        for quest in quests:
            id = quest["questID"]
            if quest.get("properties"):
                property = quest["properties"]["betterquesting"]
            else:
                property = quest
            for key in ["name", "description", "desc"]:
                if value := property.get(key):
                    lang.update(key=f"{self.modpack}.quest.{id}.{key}", value=value)
                    property[key] = f"{self.modpack}.quest.{id}.{key}"
    
    def _convert_line_v1(self, lang: QuestLang, lines: dict) -> None:
        for id, line in enumerate(lines):
            if line.get("properties"):
                id = line["lineID"]
                property = line["properties"]["betterquesting"]
            else:
                property = line
            for key in ["name", "description", "desc"]:
                if value := property.get(key):
                    lang.update(key=f"{self.modpack}.line.{id}.{key}", value=value)
                    property[key] = f"{self.modpack}.line.{id}.{key}"
    
    def _convert_quest_v2(self, lang: QuestLang, quests: dict) -> None:
        for _, quest in quests.items():
            id = quest["questID:3"]
            property = quest["properties:10"]["betterquesting:10"]
            for key in ["name:8", "desc:8"]:
                if value := property.get(key):
                    lang.update(key=f"{self.modpack}.quest.{id}.{key[:-2]}", value=value)
                    property[key] = f"{self.modpack}.quest.{id}.{key[:-2]}"

    def _convert_line_v2(self, lang: QuestLang, lines: dict) -> None:
       for _, line in lines.items():
            id = line["lineID:3"]
            property = line["properties:10"]["betterquesting:10"]
            for key in ["name:8", "desc:8"]:
                if value := property.get(key):
                    lang.update(key=f"{self.modpack}.line.{id}.{key[:-2]}", value=value)
                    property[key] = f"{self.modpack}.line.{id}.{key[:-2]}"

class QuestLocalizer(metaclass=ABCMeta):
    """Quest Localizer Class (Abstract)

    Args
    ----
        files (list[BytesIO]): The list of BytesIO objects containing the file data.
        src (str): The source language.
        dest (str): The destination language.
        modpack (str, optional): The modpack name. Defaults to "modpack".
        translate_only (bool, optional): True if only translating, False otherwise. Defaults to False.
    
    Attributes
    ----------
        src (QuestLang): The QuestLang object of the source language.
        dest (QuestLang): The QuestLang object of the destination language.
        modpack (str): The modpack name.
        quests (list[QuestData]): The list of QuestData objects.
        translate_only (bool): True if only translating, False otherwise.
    """
    src: QuestLang
    dest: QuestLang
    modpack: str
    quests: list[QuestData]
    translate_only: bool
    
    @abstractmethod
    def __init__(self, files: list[BytesIO], src: str, dest: str, modpack: str = "modpack", translate_only: bool = False) -> None:
        pass
    
    @final
    def convert_quests(self) -> None:
        """Convert the quests.
        """
        if self.translate_only:
            return
        
        for quest in ProgressBar(self.quests, task="convert"):
            quest.convert(self.src)
    
    @final
    def translate_quests(self) -> None:
        """Translate the quests.
        """
        self.src.translate(self.dest)
    
    @property
    @abstractmethod
    def src_lang(self) -> str:
        """Get the source language string.

        Returns:
            str: The source language string.
        """
        pass
    
    @property
    @abstractmethod
    def dest_lang(self) -> str:
        """Get the destination language string.

        Returns:
            str: The destination language string.
        """
        pass
    
    @property
    @abstractmethod
    def template_lang(self) -> str:
        """Get the template language string.

        Returns:
            str: The template language string.
        """
        pass

class FTBQuestLocalizer(QuestLocalizer):
    """FTB Quests Localizer Class

    Args
    ----
        files (list[BytesIO]): The list of BytesIO objects containing the file data.
        src (str): The source language.
        dest (str): The destination language.
        modpack (str, optional): The modpack name. Defaults to "modpack".
        translate_only (bool, optional): True if only translating, False otherwise. Defaults to False.
    
    Attributes
    ----------
        src (QuestLang): The QuestLang object of the source language.
        dest (QuestLang): The QuestLang object of the destination language.
        modpack (str): The modpack name.
        quests (list[FTBQuestData]): The list of FTBQuestData objects.
        translate_only (bool): True if only translating, False otherwise.
    """
    src: QuestLang
    dest: QuestLang
    modpack: str
    quests: list[FTBQuestData]
    translate_only: bool
    
    @overrides
    def __init__(self, files: list[BytesIO], src: str, dest: str, modpack: str = "modpack", translate_only: bool = False) -> None:
        self.translate_only = translate_only
        if self.translate_only:
            self.src = QuestLang(src, json=json.loads(StringIO(files[0].getvalue().decode("utf-8")).read()))
            self.dest = QuestLang(dest)
            self.modpack = None
            self.quests = None
        else:
            self.src = QuestLang(src)
            self.dest = QuestLang(dest)
            self.modpack = REGEX["strip"].sub("", modpack.lower().replace(" ", "_"))
            self.quests = [FTBQuestData(
                data = StringIO(quest.getvalue().decode("utf-8")).read(),
                modpack = self.modpack,
                chapter = os.path.splitext(quest.name)[0]
                ) for quest in files]
    
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
                zip_obj.writestr(f"{quest.chapter}.snbt", quest.data)
        return zip_dir

    @property
    @overrides
    def src_lang(self) -> str:
        """Get the JSON string of the source language.

        Returns
        -------
            str: The JSON string of the source language.
        """
        return json.dumps(self.src.json, indent=4, ensure_ascii=False)
    
    @property
    @overrides
    def dest_lang(self) -> str:
        """Get the JSON string of the destination language.

        Returns
        -------
            str: The JSON string of the destination language.
        """
        return json.dumps(self.dest.json, indent=4, ensure_ascii=False)
    
    @property
    @overrides
    def template_lang(self) -> str:
        """Get the JSON string of the template language.

        Returns
        -------
            str: The JSON string of the template language.
        """
        temp = QuestLang("template", self.src.json)
        temp.clear_values()
        return json.dumps(temp.json, indent=4, ensure_ascii=False)    

class BQMQuestLocalizer(QuestLocalizer):
    """BQM Quest Localizer Class

    Args
    ----
        files (list[BytesIO]): The list of BytesIO objects containing the file data.
        src (str): The source language.
        dest (str): The destination language.
        modpack (str, optional): The modpack name. Defaults to "modpack".
        translate_only (bool, optional): True if only translating, False otherwise. Defaults to False.
    
    Attributes
    ----------
        src (QuestLang): The QuestLang object of the source language.
        dest (QuestLang): The QuestLang object of the destination language.
        modpack (str): The modpack name.
        quests (list[BQMQuestData]): The list of FTBQuestData objects.
    """
    src: QuestLang
    dest: QuestLang
    modpack: str
    quests: list[BQMQuestData]
    
    @overrides
    def __init__(self, files: list[BytesIO], src: str, dest: str, modpack: str = "modpack", translate_only: bool = False) -> None:
        self.translate_only = translate_only
        if self.translate_only:
            self.src = QuestLang(src)
            self.src.load_from_lang(StringIO(files[0].getvalue().decode("utf-8")).read())
            self.dest = QuestLang(dest)
            self.modpack = None
            self.quests = None
        else:
            self.src = QuestLang(src)
            self.dest = QuestLang(dest)
            self.modpack = REGEX["strip"].sub("", modpack.lower().replace(" ", "_"))
            self.quests = [BQMQuestData(
                data = json.loads(StringIO(quest.getvalue().decode("utf-8")).read()),
                modpack = self.modpack
                ) for quest in files]

    @property
    @overrides
    def src_lang(self) -> str:
        """Get the LANG string of the source language.
        Returns
        -------
            str: The LANG string of the source language.
        """
        return self.src.convert_to_lang()
    
    @property
    @overrides
    def dest_lang(self) -> str:
        """Get the LANG string of the destination language.
        Returns
        -------
            str: The LANG string of the destination language.
        """
        return self.dest.convert_to_lang()

    @property
    @overrides
    def template_lang(self) -> str:
        """Get the LANG string of the template language.
        Returns
        -------
            str: The LANG string of the template language.
        """
        temp = QuestLang("template", self.src.json)
        temp.clear_values()
        return temp.convert_to_lang(allow_blank=True)
    
    @property
    def quest_json(self) -> str:
        """Get the JSON string of the quests.

        Returns
        -------
            str: The JSON string of the quests.
        """
        return json.dumps(self.quests[0].data, indent=4, ensure_ascii=False)