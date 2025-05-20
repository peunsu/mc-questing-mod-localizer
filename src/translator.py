import re
import time
from abc import abstractmethod

import deepl
import googletrans

from .constants import MINECRAFT_TO_DEEPL, MINECRAFT_TO_GOOGLE

class Translator:
    @abstractmethod
    def __init__(self):
        pass
    
    @staticmethod
    def _escape_color_code(text: str) -> str:
        return re.sub(r"(&[0-9a-z])", r"<\g<0>>", text)
    
    @staticmethod
    def _unescape_color_code(text: str) -> str:
        text = re.sub(r"(<&[0-9a-z]>)", lambda x: x.group(0)[1:-1], text)
        text = re.sub(r"&(?=[^0-9a-z]|$)", r"\&", text)
        return text
    
    def translate(self, text: str, target_lang: str) -> str:
        retry_count = 0
        retry_delay = 3
        while True:
            input_text = self._escape_color_code(text)
            try:
                output_text = self._translate(input_text, target_lang)
            except Exception as e:
                retry_count += 1
                if retry_count == 5:
                    raise e
                time.sleep(retry_delay)
                retry_delay *= 2
            return self._unescape_color_code(output_text)
    
    @abstractmethod
    def _translate(self, text: str, target_lang: str) -> str:
        pass

class GoogleTranslator(Translator):
    def __init__(self):
        self.translator = googletrans.Translator()
    
    def _translate(self, text: str, target_lang: str) -> str:
        return self.translator.translate(text, dest=MINECRAFT_TO_GOOGLE[target_lang]).text

class DeepLTranslator(Translator):
    def __init__(self, auth_key: str):
        self.translator = deepl.DeepLClient(auth_key)
    
    def _translate(self, text: str, target_lang: str) -> str:
        return self.translator.translate_text(
            text=text,
            target_lang=MINECRAFT_TO_DEEPL[target_lang],
            context="This is a Minecraft quest text, so please keep the color codes and formatting intact. Example of color codes: &a, &b, &1, &2, &l, &r. Example Translation: <&a>Hello <&b>Minecraft! -> <&a>안녕하세요 <&b>마인크래프트!",
            preserve_formatting=True,
        ).text