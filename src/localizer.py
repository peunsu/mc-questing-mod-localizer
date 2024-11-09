import os
import re
import json
import zipfile
import ftb_snbt_lib as slib

import deepl
import googletrans

from abc import abstractmethod
from time import sleep
from io import BytesIO, StringIO
from ftb_snbt_lib.tag import *

from src.components import ProgressBar
from src.constants import *

class Translator:
    @abstractmethod
    def __init__(self):
        pass
    
    def get_translator(self, name: str, auth_key: str = None) -> "Translator":
        if name == "Google":
            return GoogleTranslator()
        elif name == "DeepL":
            if not auth_key:
                raise ValueError("DeepL translator requires an authentication key")
            return DeepLTranslator(auth_key)
        else:
            raise ValueError("Invalid translator name")
    
    def escape_color_code(self, text: str) -> str:
        output = re.sub(r"(&[^0-9a-fk-or])", lambda x: x.group(0).replace("&", r"\&"), text)
        if output.endswith("&"):
            output = output[:-1] + r"\&"
        return output
    
    @abstractmethod
    def _translate(self, text: str, dest: str) -> str:
        pass
    
    def translate(self, text: str, dest: str) -> str:
        retry_count = 0
        while True:
            try:
                return self.escape_color_code(self._translate(text, dest))
            except Exception as e:
                retry_count += 1
                if retry_count == MAX_RETRY:
                    raise e
                sleep(3)
        
    
class GoogleTranslator(Translator):
    def __init__(self):
        self.translator = googletrans.Translator()
    
    def _translate(self, text: str, dest: str) -> str:
        return self.translator.translate(text, dest=MINECRAFT_TO_GOOGLE[dest]).text

class DeepLTranslator(Translator):
    def __init__(self, auth_key: str):
        self.translator = deepl.Translator(auth_key)
    
    def _translate(self, text: str, dest: str) -> str:
        return self.translator.translate_text(text, target_lang=MINECRAFT_TO_DEEPL[dest], preserve_formatting=True).text
    
class Locale:
    data: dict
    lang: str
    translator: Translator
    
    @abstractmethod
    def __init__(self, lang: str, default_data: str = None):
        pass
    
    def __getitem__(self, key: str) -> str:
        return self.data.__getitem__(key)
    
    def __setitem__(self, key: str, value: str) -> None:
        self.data.__setitem__(key, value)
    
    def __delitem__(self, key: str) -> None:
        self.data.__delitem__(key)
        
    def translate(self, translator: Translator, target: "Locale") -> None:
        if target.lang == self.lang:
            return
        for key, text in ProgressBar(self.data.items(), task="translate"):
            target[key] = self._translate(translator, text, target)
    
    def _translate(self, translator: Translator, text: str, target: "Locale") -> str:
        if not text:
            return text
        if text.startswith("[ ") and text.endswith(" ]"):
            return text
        if text.startswith("{") and text.endswith("}"):
            return text
        return translator.translate(text, dest=target.lang).replace("& ", r"\& ")
                
    @property
    def template(self) -> "Locale":
        _template = self.__class__(self.lang)
        _template.data = dict(zip(self.data.keys(), [''] * len(self.data)))
        return _template

class FTBLocale(Locale):
    data: dict
    lang: str
    translator: Translator
    
    def __init__(self, lang: str, default_data: str = None):
        self.data = json.loads(default_data) if default_data else dict()
        self.lang = lang
        self.translator = Translator()

class FTBRenewalLocale(Locale):
    data: dict
    lang: str
    translator: Translator
    
    def __init__(self, lang: str, default_data: str = None):
        self.data = slib.loads(default_data) if default_data else Compound()
        self.lang = lang
        self.translator = Translator()
    
    def translate(self, translator: Translator, target: "FTBRenewalLocale") -> None:
        if target.lang == self.lang:
            return
        for key, value in ProgressBar(self.data.items(), task="translate"):
            if isinstance(value, String):
                target[key] = String(self._translate(translator, value, target))
            elif isinstance(value, List) and issubclass(value.subtype, String):
                target[key]  = List([String('')] * len(value))
                for idx, val in enumerate(value):
                    target[key][idx] = String(self._translate(translator, val, target))
    
    @property
    def template(self) -> "FTBRenewalLocale":
        _template = self.__class__(self.lang)
        for key, value in self.data.items():
            if isinstance(value, String):
                _template[key] = String('')
            elif isinstance(value, List) and issubclass(value.subtype, String):
                _template[key] = List([String('')] * len(value))
        return _template

class BQMLocale(Locale):
    data: dict
    lang: str
    translator: Translator
    
    def __init__(self, lang: str, default_data: str = None):
        self.data = dict()
        self.lang = lang
        self.translator = Translator()
        self.load_from_lang(default_data)
    
    def load_from_lang(self, data: str):
        if not data:
            return
        for line in data.splitlines():
            if line.startswith("#") or not line:
                continue
            key, value = re.compile('(.*)=(.*)').match(line).groups()
            self[key] = value.replace("%n", "\n")

    def dump_to_lang(self) -> str:
        output = ""
        for key, value in self.data.items():
            value = value.replace('\n', r'\n')
            output += f"{key}={value}\n"
        return output

class QuestData:
    data: dict
    modpack: str
    
    @abstractmethod
    def __init__(self, data: str, modpack: str):
        pass
    
    @abstractmethod
    def convert(self, lang: Locale):
        pass

class FTBQuestData(QuestData):
    data: Compound
    modpack: str
    chapter: str
    
    ESCAPE_SUBS: dict = {
        r'%': r'%%',
        r'"': r'\"'
    }
    
    def __init__(self, data: str, modpack: str, chapter: str):
        self.data = slib.loads(data)
        self.modpack = modpack
        self.chapter = chapter

    def _filter(self, text: str) -> bool:
        if not text:
            return False
        if text.startswith("{") and text.endswith("}"):
            return False
        if text.startswith("[") and text.endswith("]"):
            return False
        return True

    def convert(self, lang: FTBLocale):
        self._convert(lang, self.data, f"{self.modpack}.{self.chapter}")
    
    def _convert(self, lang: FTBLocale, data: Compound, lang_key: str):
        if not isinstance(data, Compound):
            raise TypeError("The quest data must be a Compound type object")
        for key in filter(lambda x: data[x], data):
            if isinstance(data[key], Compound):
                self._convert(lang, data[key], f"{lang_key}.{key}")
            elif isinstance(data[key], List) and issubclass(data[key].subtype, Compound):
                for idx in range(len(data[key])):
                    self._convert(lang, data[key][idx], f"{lang_key}.{key}{idx}")
            if key in ["title", "subtitle", "description"]:
                if isinstance(data[key], String) and self._filter(data[key]):
                    lang[f"{lang_key}.{key}"] = self._escape_string(data[key])
                    data[key] = slib.String(f"{{{lang_key}.{key}}}")
                elif isinstance(data[key], List) and issubclass(data[key].subtype, String):
                    for idx, i in enumerate(filter(lambda x: self._filter(data[key][x]), range(len(data[key])))):
                        lang[f"{lang_key}.{key}{idx}"] = self._escape_string(data[key][i])
                        data[key][i] = slib.String(f"{{{lang_key}.{key}{idx}}}")
    
    def _escape_string(self, string: str) -> str:
        for match, seq in self.ESCAPE_SUBS.items():
            string = string.replace(match, seq)
        return string

class BQMQuestData(QuestData):
    data: dict
    modpack: str
    version: int = 0
    _quest_id: str
    _line_id: str
    _name: str
    _desc: str
    
    def __new__(cls, data: str, modpack: str):
        if not cls.version:
            cls = cls.infer_version(data)
        return super().__new__(cls)
    
    def __init__(self, data: str, modpack: str):
        self.data = json.loads(data)
        self.modpack = modpack
    
    def convert(self, lang: BQMLocale):
        self.convert_quests(lang)
        self.convert_questlines(lang)
    
    @staticmethod
    def infer_version(data: str):
        data = json.loads(data)
        if 'questDatabase:9' in data:
            return BQMQuestDataV1
        elif 'questDatabase' in data:
            if 'properties' in data['questDatabase'][0]:
                return BQMQuestDataV3
            else:
                return BQMQuestDataV2
        else:
            raise ValueError("The data is not a valid BQM quest data")
    
    @abstractmethod
    def convert_quests(self, lang: BQMLocale):
        pass
    
    def _convert_quests(self, lang: BQMLocale, idx: int, properties: dict):
        name, desc = self._get_name_desc(properties)
        lang[f"{self.modpack}.quests{idx}.name"] = name
        lang[f"{self.modpack}.quests{idx}.desc"] = desc
        properties[self._name] = f"{self.modpack}.quests{idx}.name"
        properties[self._desc] = f"{self.modpack}.quests{idx}.desc"
    
    @abstractmethod
    def convert_questlines(self, lang: BQMLocale):
        pass
    
    def _convert_questlines(self, lang: BQMLocale, idx: int, properties: dict):
        name, desc = self._get_name_desc(properties)        
        lang[f"{self.modpack}.questlines{idx}.name"] = name
        lang[f"{self.modpack}.questlines{idx}.desc"] = desc
        properties[self._name] = f"{self.modpack}.questlines{idx}.name"
        properties[self._desc] = f"{self.modpack}.questlines{idx}.desc"
    
    def _get_name_desc(self, properties: dict) -> tuple[str, str]:
        name = properties.get(self._name)
        desc = properties.get(self._desc)
        if not name:
            name = "No Name"
        if not desc:
            desc = "No Description"
        return name, desc
        
class BQMQuestDataV1(BQMQuestData):
    version: int = 1
    _quest_id: str = 'questID:3'
    _line_id: str = 'lineID:3'
    _name: str = 'name:8'
    _desc: str = 'desc:8'
    
    def convert_quests(self, lang: BQMLocale):
        quest_db = self.data['questDatabase:9']
        for quest in quest_db.values():
            idx = quest.get(self._quest_id)
            properties = quest['properties:10']['betterquesting:10']
            self._convert_quests(lang, idx, properties)
    
    def convert_questlines(self, lang: BQMLocale):
        questline_db = self.data['questLines:9']
        for questline in questline_db.values():
            idx = questline.get(self._line_id)
            properties = questline['properties:10']['betterquesting:10']
            self._convert_questlines(lang, idx, properties)
    
class BQMQuestDataV2(BQMQuestData):
    version: int = 2
    _quest_id: str = 'questID'
    _name: str = 'name'
    _desc: str = 'description'
    
    def convert_quests(self, lang: BQMLocale):
        quest_db = self.data['questDatabase']
        for quest in quest_db:
            idx = quest.get(self._quest_id)
            properties = quest
            self._convert_quests(lang, idx, properties)

    def convert_questlines(self, lang: BQMLocale):
        questline_db = self.data['questLines']
        for idx, questline in enumerate(questline_db):
            properties = questline
            self._convert_questlines(lang, idx, properties)

class BQMQuestDataV3(BQMQuestData):
    version: int = 3
    _quest_id: str = 'questID'
    _line_id: str = 'lineID'
    _name: str = 'name'
    _desc: str = 'desc'
    
    def convert_quests(self, lang: BQMLocale):
        quest_db = self.data['questDatabase']
        for quest in quest_db:
            idx = quest.get(self._quest_id)
            properties = quest['properties']['betterquesting']
            self._convert_quests(lang, idx, properties)
    
    def convert_questlines(self, lang: BQMLocale):
        questline_db = self.data['questLines']
        for questline in questline_db:
            idx = questline.get(self._line_id)
            properties = questline['properties']['betterquesting']
            self._convert_questlines(lang, idx, properties)

class Localizer:
    translator: Translator
    src: Locale
    dest: Locale
    modpack: str
    quests: list[QuestData]
    
    @abstractmethod
    def __init__(self, locale_data: list[BytesIO], quest_data: list[BytesIO], translator: Translator, src: str, dest: str, modpack: str):
        pass
    
    def convert(self):
        for quest in ProgressBar(self.quests, task="convert"):
            quest.convert(self.src)
    
    def translate(self):
        self.src.translate(self.translator, self.dest)
    
    def read(self, data: BytesIO) -> str:
        try:
            return StringIO(data.getvalue().decode('utf-8-sig')).read()
        except UnicodeDecodeError:
            return StringIO(data.getvalue().decode('ISO-8859-1')).read()

    def modpack_name(self, name: str) -> str:
        return re.compile('\W+').sub("", name.lower().replace(" ", "_"))
    
    @property
    def template(self) -> "Locale":
        return self.src.template

class FTBLocalizer(Localizer):
    translator: Translator
    src: FTBLocale
    dest: FTBLocale
    modpack: str
    quests: list[FTBQuestData]
    
    def __init__(self, locale_data: list[BytesIO], quest_data: list[BytesIO], translator: Translator, src: str, dest: str, modpack: str):
        self.translator = translator
        self.src = FTBLocale(src, self.read(locale_data[0])) if locale_data else FTBLocale(src)
        self.dest = FTBLocale(dest)
        self.modpack = self.modpack_name(modpack)
        self.quests = [FTBQuestData(self.read(quest), self.modpack, self.chapter_name(quest.name)) for quest in quest_data]
    
    def chapter_name(self, name: str) -> str:
        return re.compile('\W+').sub("", os.path.splitext(name)[0].lower().replace(" ", "_"))
    
    def compress_quests(self, dir: str, file_name: str) -> str:
        zip_dir = os.path.join(dir, file_name)
        with zipfile.ZipFile(zip_dir, 'w') as zip_obj:
            for quest in self.quests:
                zip_obj.writestr(f"{quest.chapter}.snbt", slib.dumps(quest.data))
        return zip_dir
    
class FTBRenewalLocalizer(Localizer):
    translator: Translator
    src: FTBLocale
    dest: FTBLocale
    
    def __init__(self, locale_data: list[BytesIO], quest_data: list[BytesIO], translator: Translator, src: str, dest: str, modpack: str):
        self.translator = translator
        self.src = FTBRenewalLocale(src, self.read(locale_data[0])) if locale_data else FTBRenewalLocale(src)
        self.dest = FTBRenewalLocale(dest)
    
    def convert(self):
        return

class BQMLocalizer(Localizer):
    translator: Translator
    src: BQMLocale
    dest: BQMLocale
    modpack: str
    quests: list[BQMQuestData]
    
    def __init__(self, locale_data: list[BytesIO], quest_data: list[BytesIO], translator: Translator, src: str, dest: str, modpack: str):
        self.translator = translator
        self.src = BQMLocale(src, self.read(locale_data[0])) if locale_data else BQMLocale(src)
        self.dest = BQMLocale(dest)
        self.modpack = self.modpack_name(modpack)
        self.quests = [BQMQuestData(self.read(quest), self.modpack) for quest in quest_data]
