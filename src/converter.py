import re
import os
import json
import ftb_snbt_lib as slib

from abc import abstractmethod
from io import BytesIO
from zipfile import ZipFile
from ftb_snbt_lib import tag
from src.utils import read_file

class QuestConverter():
    def __init__(self, modpack_name: str, quest_arr: list[BytesIO]):
        self.modpack_name = modpack_name
        self.quest_arr = [self._read(quest) for quest in quest_arr]
        self.lang_dict = {}
    
    @staticmethod
    @abstractmethod
    def _read(quest: BytesIO) -> tuple:
        pass
    
    @abstractmethod
    def convert(self) -> tuple[list, dict]:
        pass

class FTBQuestConverter(QuestConverter):
    @staticmethod
    def _read(quest: BytesIO) -> tuple[str, tag.Compound]:
        quest_name = re.compile(r'\W+').sub("", os.path.splitext(quest.name)[0].lower().replace(" ", "_"))
        
        quest_data = read_file(quest)
        quest_data = slib.loads(quest_data)
        if not isinstance(quest_data, tag.Compound):
            raise TypeError("The quest data must be a Compound tag object")
        
        return quest_name, quest_data
    
    def convert(self) -> tuple[list, dict]:
        for quest_name, quest_data in self.quest_arr:
            self._convert(quest_data, f"{self.modpack_name}.{quest_name}")
        return self.quest_arr, self.lang_dict
    
    def _convert(self, quest_data: tag.Compound, lang_key: str):
        for element in filter(lambda x: quest_data[x], quest_data):
            if isinstance(quest_data[element], tag.Compound):
                self._convert(quest_data[element], f"{lang_key}.{element}")
            elif isinstance(quest_data[element],tag.List) and issubclass(quest_data[element].subtype, tag.Compound):
                for idx in range(len(quest_data[element])):
                    self._convert(quest_data[element][idx], f"{lang_key}.{element}{idx}")
            
            if element in ("title", "subtitle", "description"):
                if isinstance(quest_data[element], tag.String) and self._filter(quest_data[element]):
                    self.lang_dict[f"{lang_key}.{element}"] = self._escape(quest_data[element])
                    quest_data[element] = tag.String(f"{{{lang_key}.{element}}}")
                elif isinstance(quest_data[element], tag.List) and issubclass(quest_data[element].subtype, tag.String):
                    for lang_idx, data_idx in enumerate(filter(lambda x: self._filter(quest_data[element][x]), range(len(quest_data[element])))):
                        self.lang_dict[f"{lang_key}.{element}{lang_idx}"] = self._escape(quest_data[element][data_idx])
                        quest_data[element][data_idx] = tag.String(f"{{{lang_key}.{element}{lang_idx}}}")
    
    @staticmethod
    def _filter(quest_str: tag.String) -> bool:
        if not quest_str:
            return False
        if quest_str.startswith("{") and quest_str.endswith("}"):
            return False
        if quest_str.startswith("[") and quest_str.endswith("]"):
            return False
        return True
    
    @staticmethod
    def _escape(quest_str: tag.String) -> str:
        for match, seq in ((r'%', r'%%'), (r'"', r'\"')):
            quest_str = quest_str.replace(match, seq)
        return quest_str
    
    def compress(self, dir: str, filename: str) -> str:
        zip_dir = os.path.join(dir, filename)
        with ZipFile(zip_dir, "w") as zip_file:
            for quest_name, quest_data in self.quest_arr:
                zip_file.writestr(f"{quest_name}.snbt", slib.dumps(quest_data))
        return zip_dir

class BQMQuestConverter(QuestConverter):
    @staticmethod
    def _read(quest: BytesIO) -> tuple[int, dict]:
        quest_data = read_file(quest)
        quest_data = json.loads(quest_data)
        if not isinstance(quest_data, dict):
            raise TypeError("The quest data must be a json object")

        if 'questDatabase:9' in quest_data:
            quest_version = 1
        elif 'questDatabase' in quest_data:
            if 'properties' in quest_data['questDatabase'][0]:
                quest_version = 3
            else:
                quest_version = 2
        else:
            raise ValueError("The quest data is not a valid format")
        
        return quest_version, quest_data
    
    def convert(self) -> tuple[list, dict]:
        for quest_version, quest_data in self.quest_arr:
            self._convert(quest_version, quest_data)
        return self.quest_arr, self.lang_dict
    
    def _convert(self, quest_version: int, quest_data: dict):
        match quest_version:
            case 1:
                self._convert_v1(quest_data)
            case 2:
                self._convert_v2(quest_data)
            case 3:
                self._convert_v3(quest_data)
    
    def _convert_v1(self, quest_data: dict):        
        quest_db = quest_data['questDatabase:9']
        for quest in quest_db.values():
            idx = quest.get('questID:3')
            properties = quest['properties:10']['betterquesting:10']
            self._update_quest(properties, idx, 'name:8', 'desc:8')
        
        questline_db = quest_data['questLines:9']
        for questline in questline_db.values():
            idx = questline.get('lineID:3')
            properties = questline['properties:10']['betterquesting:10']
            self._update_questline(properties, idx, 'name:8', 'desc:8')
    
    def _convert_v2(self, quest_data: dict):
        quest_db = quest_data['questDatabase']
        for quest in quest_db:
            idx = quest.get('questID')
            properties = quest
            self._update_quest(properties, idx, 'name', 'description')
        
        questline_db = quest_data['questLines']
        for idx, questline in enumerate(questline_db):
            properties = questline
            self._update_questline(properties, idx, 'name', 'description')
            
    def _convert_v3(self, quest_data: dict):
        quest_db = quest_data['questDatabase']
        for quest in quest_db:
            idx = quest.get('questID')
            properties = quest['properties']['betterquesting']
            self._update_quest(properties, idx, 'name', 'desc')
        
        questline_db = quest_data['questLines']
        for questline in questline_db:
            idx = questline.get('lineID')
            properties = questline['properties']['betterquesting']
            self._update_questline(properties, idx, 'name', 'desc')
    
    @staticmethod
    def _get_property(properties: dict, name_key: str, desc_key: str) -> tuple[str, str]:
        name = properties.get(name_key)
        desc = properties.get(desc_key)
        
        if not name:
            name = 'No Name'
        if not desc:
            desc = 'No Description'
        
        return name, desc
    
    def _update_quest(self, properties: dict, idx: int, name_key: str, desc_key: str):
        name, desc = self._get_property(properties, name_key, desc_key)
        
        self.lang_dict[f"{self.modpack_name}.quests{idx}.name"] = name
        self.lang_dict[f"{self.modpack_name}.quests{idx}.desc"] = desc
        properties[name_key] = f"{self.modpack_name}.quests{idx}.name"
        properties[desc_key] = f"{self.modpack_name}.quests{idx}.desc"
    
    def _update_questline(self, properties: dict, idx: int, name_key: str, desc_key: str):
        name, desc = self._get_property(properties, name_key, desc_key)
        
        self.lang_dict[f"{self.modpack_name}.questlines{idx}.name"] = name
        self.lang_dict[f"{self.modpack_name}.questlines{idx}.desc"] = desc
        properties[name_key] = f"{self.modpack_name}.questlines{idx}.name"
        properties[desc_key] = f"{self.modpack_name}.questlines{idx}.desc"
    
class SNBTConverter:
    @staticmethod
    def convert_snbt_to_json(tag: slib.Compound) -> dict:
        return json.loads(json.dumps(tag, ensure_ascii=False))

    @staticmethod
    def convert_json_to_snbt(data: dict) -> slib.Compound:
        output = slib.Compound()
        for key, value in data.items():
            if isinstance(value, str):
                output[key] = slib.String(value)
            elif isinstance(value, list):
                output[key]  = slib.List([slib.String('')] * len(value))
                for idx, val in enumerate(value):
                    output[key][idx] = slib.String(val)
        return output

class LANGConverter:
    @staticmethod
    def convert_lang_to_json(data: str) -> dict:
        output = {}
        for line in data.splitlines():
            if line.startswith("#") or not line:
                continue
            key, value = re.compile('(.*)=(.*)').match(line).groups()
            output[key] = value.replace("%n", r"\n")
        return output

    @staticmethod
    def convert_json_to_lang(data: dict) -> str:
        output = ""
        for key, value in data.items():
            value = value.replace(r"\n", "%n")
            output += f"{key}={value}\n"
        return output