import re
import time
from abc import abstractmethod

import deepl
import googletrans

from .constants import MINECRAFT_TO_DEEPL, MINECRAFT_TO_GOOGLE

class Translator:
    @abstractmethod
    def __init__(self, target_lang: str):
        pass
    
    @staticmethod
    def _escape_color_code(text: str) -> str:
        return re.sub(r"(&[0-9a-z])", r"<\g<0>>", text)
    
    @staticmethod
    def _unescape_color_code(text: str) -> str:
        return re.sub(r"(<&[0-9a-z]>)", lambda x: x.group(0)[1:-1], text)
    
    def translate(self, text: str) -> str:
        retry_count = 0
        retry_delay = 3
        while True:
            input_text = self._escape_color_code(text)
            try:
                output_text = self._translate(input_text)
            except Exception as e:
                retry_count += 1
                if retry_count == 5:
                    raise e
                time.sleep(retry_delay)
                retry_delay *= 2
            return self._unescape_color_code(output_text)
    
    @abstractmethod
    def _translate(self, text: str) -> str:
        pass

class GoogleTranslator(Translator):
    def __init__(self, target_lang: str):
        self.translator = googletrans.Translator()
        self.target_lang = target_lang
    
    def _translate(self, text: str) -> str:
        return self.translator.translate(text, dest=MINECRAFT_TO_GOOGLE[self.target_lang]).text

class DeepLTranslator(Translator):
    def __init__(self, target_lang: str, auth_key: str):
        self.translator = deepl.DeepLClient(auth_key)
        self.target_lang = target_lang
    
    def _translate(self, text: str) -> str:
        return self.translator.translate_text(
            text=text,
            target_lang=MINECRAFT_TO_DEEPL[self.target_lang],
            context="This is a Minecraft quest text, so please keep the color codes and formatting intact. Example of color codes: &a, &b, &1, &2, &l, &r. Example Translation: <&a>Hello <&b>Minecraft! -> <&a>안녕하세요 <&b>마인크래프트!",
            preserve_formatting=True,
        ).text