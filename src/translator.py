import re
import json
import asyncio
import logging
from abc import abstractmethod
from flatten_json import flatten, unflatten_list
from tenacity import retry, stop_after_attempt, wait_exponential

import googletrans
import deepl
import tiktoken
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI

from src.utils import stqdm_asyncio, get_session_id
from src.constants import MINECRAFT_TO_DEEPL, MINECRAFT_TO_GOOGLE

class Translator:
    def __init__(self):        
        self.logger = logging.getLogger(f"{self.__class__.__qualname__} ({get_session_id()})")
        self.logger.info("Initialized")

    @staticmethod
    def _escape(text: str) -> str:
        text = re.sub(r"(\\n)", r"<br>", text) # escape newline
        return re.sub(r"(&[0-9a-z])", lambda x: f"<{x.group(0)[1:]}>", text) # escape color code
    
    @staticmethod
    def _unescape(text: str) -> str:
        text = re.sub(r"(<[0-9a-zA-Z]>)", lambda x: f"&{x.group(0)[1:-1].lower()}", text) # restore color code
        text = re.sub(r"&(?=[^0-9a-z]|$)", r"\&", text) # escape single &
        text = re.sub(r"(<br>|<BR>)", r"\\n", text) # restore newline
        return text

    def make_batches(self, lang_dict: dict, max_tokens: int) -> list:
        batches = []
        current_batch = {}
        current_tokens = 0
        enc = tiktoken.encoding_for_model("gpt-4")
        
        for key, value in lang_dict.items():
            pair_str = json.dumps({key: value}, ensure_ascii=False)
            tokens = len(enc.encode(pair_str)) # count tokens
            if current_tokens + tokens > max_tokens and current_batch:
                batches.append(current_batch) # append current batch
                current_batch = {}
                current_tokens = 0

            current_batch[key] = value # add to current batch if not exceeding max tokens
            current_tokens += tokens
        
        if current_batch: # append the last batch
            batches.append(current_batch)

        self.logger.info("Created %d batches", len(batches))

        return batches
    
    async def translate(self, source_lang_dict: dict, target_lang_dict: dict, target_lang: str, status):        
        async def wrap_translate(idx, batch):
            await asyncio.sleep(idx * 5) # 5 sec delay between requests
            
            task_name = asyncio.current_task().get_name()
            try:
                self.logger.info("Translating batch (%s)", task_name)
                return await self._translate(batch, target_lang)
            except Exception:
                batch_keys = list(batch.keys())
                batch_start = batch_keys[0] if batch_keys else None
                batch_end = batch_keys[-1] if batch_keys else None
                
                status.error(f"Translation failed for batch: `{batch_start}` ~ `{batch_end}`.")
                self.logger.error("Failed to translate batch (%s)", task_name, exc_info=True)

                return batch

        # Flatten json
        source_lang_dict_flatten = flatten(source_lang_dict, separator="|")
        
        batches = self.make_batches(source_lang_dict_flatten, max_tokens=6000) # 6000 tokens max
        batches_out = await stqdm_asyncio.gather(*[wrap_translate(idx, batch) for idx, batch in enumerate(batches)], desc="Progress", unit="batch", st_container=status, backend=False, frontend=True)

        # Unflatten json
        result = {}
        for out in batches_out:
            result.update(out)
        result = unflatten_list(result, separator="|")
        
        target_lang_dict.update(result)

        self.logger.info("Translated %d batches", len(batches_out))

    @abstractmethod
    async def _translate(self, batch: str, target_lang: str) -> dict:
        pass

class GoogleTranslator(Translator):
    def __init__(self):
        self.translator = googletrans.Translator()
        super().__init__()
    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=4, max=64), reraise=True)
    async def _translate(self, batch: dict, target_lang: str) -> dict:
        batch_input_keys = [] # keys to translate
        batch_input_values = [] # values to translate
        batch_original = {} # formatted text - do not translate
        batch_translated = {} # translated text

        for key, value in batch.items():
            if not isinstance(value, str):
                batch_original[key] = value
            elif value.startswith("[") and value.endswith("]"):
                batch_original[key] = value
            elif value.startswith("{") and value.endswith("}"):
                batch_original[key] = value
            else:
                batch_input_keys.append(key)
                batch_input_values.append(self._escape(value))

        if batch_input_values:
            batch_output = await self.translator.translate(batch_input_values, dest=MINECRAFT_TO_GOOGLE[target_lang])
            batch_translated = {key: self._unescape(value.text) for key, value in zip(batch_input_keys, batch_output)}
        return {**batch_original, **batch_translated}

class DeepLTranslator(Translator):
    def __init__(self, auth_key: str):
        self.translator = deepl.DeepLClient(auth_key)
        super().__init__()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=4, max=64), reraise=True)
    async def _translate(self, batch: dict, target_lang: str) -> dict:
        batch_input_keys = []
        batch_input_values = []
        batch_original = {}
        batch_translated = {}
        
        for key, value in batch.items():
            if not isinstance(value, str):
                batch_original[key] = value
            elif value.startswith("[") and value.endswith("]"):
                batch_original[key] = value
            elif value.startswith("{") and value.endswith("}"):
                batch_original[key] = value
            else:
                batch_input_keys.append(key)
                batch_input_values.append(self._escape(value))

        if batch_input_values:
            batch_output = await asyncio.to_thread(
                self.translator.translate_text,
                text=batch_input_values,
                target_lang=MINECRAFT_TO_DEEPL[target_lang],
                context="This is a Minecraft quest text, so please keep the color codes and formatting intact. Example of color codes: <a>, <b>, <1>, <2>, <l>, <r>. Example of formatting: <br>. Example Translation: <a>Hello <br><b>Minecraft! -> <a>안녕하세요 <br><b>마인크래프트!",
                preserve_formatting=True
            )
            batch_translated = {key: self._unescape(value.text) for key, value in zip(batch_input_keys, batch_output)}
        return {**batch_original, **batch_translated}

class GeminiTranslator(Translator):
    def __init__(self, auth_key: str):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=auth_key,
            temperature=0
        )
        content_extractor = RunnableLambda(lambda msg: getattr(msg, 'content', '') if isinstance(msg, AIMessage) else str(msg)) # extract content
        json_extractor = RunnableLambda(self.extract_json) # extract json string
        json_parser = JsonOutputParser() # parse json
        prompt = PromptTemplate(
            template="""You are a Minecraft modpack quest translation assistant.
            Your task is to translate the given JSON-formatted text.
            Be aware that what you are translating is a quest text for Minecraft modpack.
            You MUST keep the color codes INTACT. Example of color codes: &a, &b, &1, &2, &l, &r.
            You MUST keep the new line symbol (\\n) INTACT.
            Text enclosed in [] or {{}} must be kept UNCHANGED.
            If there are words that are difficult or ambiguous to translate, translate them PHONETICALLY. Also, transcribe proper nouns PHONETICALLY.
            Translation Examples (en_us -> ko_kr):
            - &aDiamond Pickaxe&r -> &a다이아몬드 곡괭이&r
            - While the &aUpgrade Template&r is not needed to make the initial tool, it will save you a lot of &6Allthemodium Ingots&r! -> &a업그레이드 템플릿&r은 초기 도구를 만드는 데 필요하지 않지만, &6올더모듐 주괴&r를 많이 절약할 수 있습니다!
            Format instructions: {format_instructions}
            Translate the following JSON-formatted text to {target_lang}, but KEEP THE KEYS EXACTLY THE SAME:
            ```json
            {query}
            ```""",
            input_variables=["target_lang", "query"],
            partial_variables={"format_instructions": json_parser.get_format_instructions()}
        )
        self.translator = prompt | llm | content_extractor | json_extractor | json_parser
        self.handler = LLMCallbackHandler(self.__class__.__qualname__)
        super().__init__()
    
    @staticmethod
    def extract_json(text: str) -> dict:
        '''
        Copyright 2025 moonzoo
        
        https://mz-moonzoo.tistory.com/m/89
        '''
        if isinstance(text, str):
            # find json code block
            if text.strip().startswith("```json"):
                start_block = text.find("{")
                end_block = text.rfind("}")
                if start_block != -1 and end_block != -1 and start_block < end_block:
                    json_str = text[start_block:end_block+1]
                    try:
                        json.loads(json_str)
                        return json_str
                    except json.JSONDecodeError:
                        pass
            
            # find the last potential json string
            start = text.rfind('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and start < end:
                json_str = text[start:end+1]
                try:
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format.")
            elif text.strip() == '{}':
                return "{}"
            else:
                raise ValueError("Invalid JSON format.")
        else:
            raise ValueError("Input must be a string.")

    # Langchain automatically retries failed requests
    async def _translate(self, batch: dict, target_lang: str) -> dict:
        batch_output = await self.translator.ainvoke(
            {
                "target_lang": target_lang,
                "query": json.dumps(batch, ensure_ascii=False)
            },
            config={
                "callbacks": [self.handler],
                "verbose": True
            }
        )
        return batch_output

class LLMCallbackHandler(BaseCallbackHandler):
    def __init__(self, cls_name, *args, **kwargs):
        self.logger = logging.getLogger(f"{cls_name} ({get_session_id()})")
        super().__init__(*args, **kwargs)

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.logger.info("LLM started: %s", serialized)

    def on_llm_error(self, error, **kwargs):
        self.logger.error("LLM error: %s", error)

    def on_retry(self, retry_state, **kwargs):
        self.logger.warning("LLM retrying: %s", retry_state)