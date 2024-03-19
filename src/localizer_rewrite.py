import ftb_snbt_lib as slib
import json
import re
from ftb_snbt_lib.tag import *
from time import sleep
from googletrans import Translator
#from .components import ProgressBar
#from .constants import MINECRAFT_TO_GOOGLE, MAX_RETRY
from constants import MINECRAFT_TO_GOOGLE, MAX_RETRY
from abc import abstractmethod

# To-do: move to constants.py
ESCAPE_SUBS = {
    r'%': r'%%',
    r'"': r'\"'
}

def load_from_lang(data: str) -> dict:
    output = dict()
    for line in data.splitlines():
        if line.startswith("#") or not line:
            continue
        key, value = re.compile('(.*)=(.*)').match(line).groups()
        output[key] = value.replace("%n", "\n")
    return output

def dump_to_lang(data: dict) -> str:
    output = ""
    for key, value in data.items():
        value = value.replace("\n", "%n").replace("=", "==")
        output += f"{key}={value}\n"
    return output

class Locale:
    data: dict
    lang: str
    translator: Translator
    
    def __getitem__(self, key: str) -> str:
        return self.data.__getitem__(key)
    
    def __setitem__(self, key: str, value: str) -> None:
        self.data.__setitem__(key, value)
    
    def __delitem__(self, key: str) -> None:
        self.data.__delitem__(key)
        
    def translate(self, target: "FTBLocale") -> None:
        if target.lang == self.lang:
            return
        #for key, text in ProgressBar(self.data.items(), task="translate"):
        for key, text in self.data.items():
            if text.startswith("[ ") and text.endswith(" ]"):
                target[key] = text
            target[key] = self._translate(target, text)
    
    def _translate(self, target: "FTBLocale", text: str) -> str:
        retry_count = 0
        while True:
            try:
                return self.translator.translate(text, dest=MINECRAFT_TO_GOOGLE[target.lang]).text
            except Exception as e:
                retry_count += 1
                if retry_count == MAX_RETRY:
                    raise e
                sleep(3)
    
    @property
    def template(self) -> dict:
        return dict(zip(self.data.keys(), [''] * len(self.data)))

class FTBLocale(Locale):
    data: dict
    lang: str
    translator: Translator
    
    def __init__(self, lang: str, default_data: str = None):
        self.data = json.loads(default_data) if default_data else dict()
        self.lang = lang
        self.translator = Translator()

class BQMLocale(Locale):
    data: dict
    lang: str
    translator: Translator
    
    def __init__(self, lang: str, default_data: str = None):
        self.data = load_from_lang(default_data) if default_data else dict()
        self.lang = lang
        self.translator = Translator()

class QuestData:
    data: dict
    modpack: str
    
    @abstractmethod
    def convert(self, lang: Locale):
        pass

class FTBQuestData(QuestData):
    data: Compound
    modpack: str
    chapter: str
    
    def __init__(self, data: str, modpack: str):
        self.data = slib.loads(data)
        self.modpack = modpack
        self.chapter = self.data['filename']
    
    def convert(self, lang: FTBLocale):
        self._convert(lang, self.data, f"{self.modpack}.{self.chapter}")
    
    def _convert(self, lang: FTBLocale, data: Compound, lang_key: str):
        if not isinstance(data, Compound):
            raise TypeError("The quest data must be a Compound type object")
        for key in data:
            if isinstance(data[key], Compound):
                self._convert(lang, data[key], f"{lang_key}.{key}")
            elif isinstance(data[key], List) and issubclass(data[key].subtype, Compound):
                for idx in range(len(data[key])):
                    self._convert(lang, data[key][idx], f"{lang_key}.{key}{idx}")
            if key in ["title", "subtitle", "description"]:
                if isinstance(data[key], String) and data[key]:
                    lang[f"{lang_key}.{key}"] = self._escape_string(data[key])
                    data[key] = slib.String(f"{{{lang_key}.{key}}}")
                elif isinstance(data[key], List) and issubclass(data[key].subtype, String):
                    for idx, i in enumerate(filter(lambda x: data[key][x], range(len(data[key])))):
                        lang[f"{lang_key}.{key}{idx}"] = self._escape_string(data[key][i])
                        data[key][i] = slib.String(f"{{{lang_key}.{key}{idx}}}")
    
    def _escape_string(self, string: str) -> str:
        for match, seq in ESCAPE_SUBS.items():
            string = string.replace(match, seq)
        return string

class BQMQuestData(QuestData):
    data: dict
    modpack: str
    version: int = 0
    
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
        lang[f"{self.modpack}.quests{idx}.name"] = properties[self.name]
        lang[f"{self.modpack}.quests{idx}.desc"] = properties[self.desc]
        properties[self.name] = f"{{{self.modpack}.quests{idx}.name}}"
        properties[self.desc] = f"{{{self.modpack}.quests{idx}.desc}}"
    
    @abstractmethod
    def convert_questlines(self, lang: BQMLocale):
        pass
    
    def _convert_questlines(self, lang: BQMLocale, idx: int, properties: dict):
        lang[f"{self.modpack}.questlines{idx}.name"] = properties.get(self.name, '')
        lang[f"{self.modpack}.questlines{idx}.desc"] = properties.get(self.desc, '')
        properties[self.name] = f"{{{self.modpack}.questlines{idx}.name}}"
        properties[self.desc] = f"{{{self.modpack}.questlines{idx}.desc}}"
        
class BQMQuestDataV1(BQMQuestData):
    version: int = 1
    quest_id: str = 'questID:3'
    line_id: str = 'lineID:3'
    name: str = 'name:8'
    desc: str = 'desc:8'
    
    def convert_quests(self, lang: BQMLocale):
        quest_db = self.data['questDatabase:9']
        for quest in quest_db.values():
            idx = quest.get(self.quest_id)
            properties = quest['properties:10']['betterquesting:10']
            self._convert_quests(lang, idx, properties)
    
    def convert_questlines(self, lang: BQMLocale):
        questline_db = self.data['questLines:9']
        for questline in questline_db.values():
            idx = questline.get(self.line_id)
            properties = questline['properties:10']['betterquesting:10']
            self._convert_questlines(lang, idx, properties)
    
class BQMQuestDataV2(BQMQuestData):
    version: int = 2
    quest_id: str = 'questID'
    name: str = 'name'
    desc: str = 'description'
    
    def convert_quests(self, lang: BQMLocale):
        quest_db = self.data['questDatabase']
        for quest in quest_db:
            idx = quest.get(self.quest_id)
            properties = quest
            self._convert_quests(lang, idx, properties)

    def convert_questlines(self, lang: BQMLocale):
        questline_db = self.data['questLines']
        for idx, questline in enumerate(questline_db):
            properties = questline
            self._convert_questlines(lang, idx, properties)

class BQMQuestDataV3(BQMQuestData):
    version: int = 3
    quest_id: str = 'questID'
    line_id: str = 'lineID'
    name: str = 'name'
    desc: str = 'desc'
    
    def convert_quests(self, lang: BQMLocale):
        quest_db = self.data['questDatabase']
        for quest in quest_db:
            idx = quest.get(self.quest_id)
            properties = quest['properties']['betterquesting']
            self._convert_quests(lang, idx, properties)
    
    def convert_questlines(self, lang: BQMLocale):
        questline_db = self.data['questLines']
        for questline in questline_db:
            idx = questline.get(self.line_id)
            properties = questline['properties']['betterquesting']
            self._convert_questlines(lang, idx, properties)

def ftbq_test():
    questData = FTBQuestData(open('tests/ftbq/mekanism.snbt').read(), 'atm9')
    questLang = FTBLocale('en_us')
    questTarget = FTBLocale('ko_kr')
    questData.convert(questLang)
    #questLang.translate(questTarget)
    slib.dump(questData.data, open('tests/ftbq/test.snbt', 'w'))
    json.dump(questLang.data, open('tests/ftbq/test.json', 'w'), indent=4, ensure_ascii=False)
    #json.dump(questTarget.data, open('tests/test_translate.json', 'w'), indent=4, ensure_ascii=False)
    json.dump(questLang.template, open('tests/ftbq/test_template.json', 'w'), indent=4, ensure_ascii=False)

def bqm_test():
    questData = BQMQuestData(open('tests/bqm/bqm_v1.json').read(), 'po3')
    #questData = BQMQuestData(open('tests/bqm/bqm_v2.json').read(), 'po3')
    #questData = BQMQuestData(open('tests/bqm/bqm_v3.json').read(), 'po3')
    questLang = BQMLocale('en_us')
    questTarget = BQMLocale('ko_kr')
    questData.convert(questLang)
    questLang.translate(questTarget)
    json.dump(questData.data, open('tests/bqm/data_bqm.json', 'w'), indent=4, ensure_ascii=False)
    json.dump(questLang.data, open('tests/bqm/lang_bqm.json', 'w'), indent=4, ensure_ascii=False)
    with open('tests/bqm/lang_bqm.lang', 'w', encoding='utf-8-sig') as f:
        f.write(dump_to_lang(questLang.data))
    json.dump(questTarget.data, open('tests/bqm/target_bqm.json', 'w'), indent=4, ensure_ascii=False)
    with open('tests/bqm/target_lang_bqm.lang', 'w', encoding='utf-8-sig') as f:
        f.write(dump_to_lang(questTarget.data))

if __name__ == "__main__":
    #ftbq_test()
    bqm_test()