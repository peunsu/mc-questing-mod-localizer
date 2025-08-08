import re
import asyncio
from src.utils import stqdm_asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
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
    
    async def translate(self, source_lang_dict: list, target_lang_dict: list, target_lang: str, status):
        semaphore = asyncio.Semaphore(4)
        
        async def wrap_translate(text):
            async with semaphore:
                await asyncio.sleep(1)
                return await loop.run_in_executor(None, self._translate, text, target_lang)

        loop = asyncio.get_running_loop()
        result = await stqdm_asyncio.gather(*[wrap_translate(text) for text in source_lang_dict.values()], st_container=status, backend=False, frontend=True)
        for key, text in zip(source_lang_dict.keys(), result):
            target_lang_dict[key] = text

    @abstractmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=16))
    def _translate(self, text: str, target_lang: str) -> str:
        pass

class GoogleTranslator(Translator):
    def __init__(self):
        self.translator = googletrans.Translator()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=16))
    def _translate(self, text: str, target_lang: str) -> str:
        text = self._escape_color_code(text)
        output = self.translator.translate(text, dest=MINECRAFT_TO_GOOGLE[target_lang]).text
        return self._unescape_color_code(output)

class DeepLTranslator(Translator):
    def __init__(self, auth_key: str):
        self.translator = deepl.DeepLClient(auth_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=16))
    def _translate(self, text: str, target_lang: str) -> str:
        text = self._escape_color_code(text)
        output = self.translator.translate_text(
            text=text,
            target_lang=MINECRAFT_TO_DEEPL[target_lang],
            context="This is a Minecraft quest text, so please keep the color codes and formatting intact. Example of color codes: &a, &b, &1, &2, &l, &r. Example Translation: <&a>Hello <&b>Minecraft! -> <&a>안녕하세요 <&b>마인크래프트!",
            preserve_formatting=True,
        ).text
        return self._unescape_color_code(output)