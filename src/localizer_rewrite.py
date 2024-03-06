from googletrans import Translator
import ftb_snbt_lib as slib

class Locale:
    data: dict
    lang: str
    translator: Translator

class FTBLocale(Locale):
    data: dict
    lang: str
    translator: Translator

class BQMLocale(Locale):
    data: dict
    lang: str
    translator: Translator

class QuestData:
    data: dict
    modpack: str

class FTBQuestData(QuestData):
    data: dict
    modpack: str
    chapter: str
    id: int
    
    def __init__(self, data: str, modpack: str):
        self.data = slib.loads(data)
        self.modpack = modpack
        self.chapter = self.data['filename']
        self.id = 0
    
    def convert(self, lang):
        self._convert(lang, self.data, f"{self.modpack}.{self.chapter}")
    
    def _convert(self, lang, data: dict, lang_key: str) -> dict:
        if isinstance(data, dict):
            self.id += 1
            for key in data:
                if isinstance(data[key], dict):
                    self._convert(lang, data[key], f"{lang_key}.{key}")
                elif isinstance(data[key], list):
                    if issubclass(data[key].subtype, str):
                        for i in range(len(data[key])):
                            data[key][i] = slib.String(f"{{{lang_key}.{key}{i}}}")
                    elif issubclass(data[key].subtype, dict):
                        for i in range(len(data[key])):
                            self._convert(lang, data[key][i], f"{lang_key}.{key}{i}")
                elif isinstance(data[key], str):
                    data[key] = slib.String(f"{{{lang_key}.{key}}}")
        

class BQMQuestData(QuestData):
    data: dict
    modpack: str
    
    
if __name__ == "__main__":
    questdata = FTBQuestData(open('tests/mekanism.snbt').read(), 'atm9')
    questdata.convert('en')
    slib.dump(questdata.data, open('tests/test.snbt', 'w'))