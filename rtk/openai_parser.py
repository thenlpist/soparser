import random
from typing import Optional
import logging
import os
import time

from openai import OpenAI

from rtk.resume_dataclass import Resume, ResumeSerializer
from rtk.validation import Validation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create file handler that logs debug and higher level messages
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)


class OAiParser:
    OPENAI_PARSER_NAME = "openai"
    OPENAI_FAIL_NAME = "openai-error"

    def __init__(self, openai_key, config: Optional[dict]):
        self.config = config
        self.validate = Validation()
        self.model = "gpt-4o-2024-08-06"
        openai_key = openai_key if openai_key else os.environ.get("OPENAI_API_KEY", None)
        self.openai_is_available = True
        if not openai_key:
            logger.error("API_KEY_NOT_DEFINED: OpenAI API key is not defined as an environment variable")
            self.openai_is_available = False
        self.client = OpenAI(api_key=openai_key)
        self.serializer = ResumeSerializer()

    def parse(self, text):
        valid_key = self._validate_key()
        if not valid_key:
            return {"parser": self.OPENAI_FAIL_NAME,
                    "is_valid_json": False,
                    "is_valid_jsonresume": False,
                    "jsonresume": {}}
        head = text[:100].replace("\n", " ")
        logger.info(f"Calling OpenAI parser for text: {head}...")
        resume, prompt_tokens, completion_tokens, generation_time = self._query_openai(text)
        num_tokens = prompt_tokens + completion_tokens
        num_chars = len(text)
        logger.debug("Validating returned object...")
        valid_json, valid_json_resume = self.validate.validate_json_w_pydantic(resume)
        try:
            name = resume["basics"]["name"]
        except:
            name = ""
        logger.info(
            f"name: `{name}`,  parser: {self.OPENAI_PARSER_NAME}, valid_json: {valid_json}, valid_jsonresume: {valid_json_resume}, num_chars: {num_chars}, num_tokens: {num_tokens}, generation_time: {generation_time} ")

        return {
            "parser": self.OPENAI_PARSER_NAME,
            "is_valid_json": valid_json,
            "is_valid_jsonresume": valid_json_resume,
            "generation_time": generation_time,
            "num_chars": num_chars,
            "num_tokens": num_tokens,
            "jsonresume": resume
        }

    def parse_standalone(self, text):
        text = self._perturb_text(text)
        response = self.parse(text)
        response, statuscode = self.validate.compute_statuscode(response)
        response["statuscode"] = statuscode
        return response

    def _perturb_text(self, text):
        if self.config.get("test", False):
            if random.random() < 0.5:
                logger.debug("Perturb 1")
                text = text[:3000]
            elif random.random() < 0.3:
                logger.debug("Perturb 2")
                text = text.replace("\n", " ")
            elif random.random() < 0.3:
                logger.debug("Perturb 3")
                items = text.split("\n")
                num_items = len(items)
                third = int(num_items / 3) * 2
                start = items[:third]
                end = items[third:]
                random.shuffle(end)
                new_items = start + end
                return "\n".join(new_items)
        return text

    def _validate_key(self):
        if self.openai_is_available == False:
            logger.error("(OAiParser) OpenAI Key is not defined")
            return False
        return True

    def _query_openai(self, text):
        t1 = time.time()
        try:
            resume_obj, prompt_tokens, completion_tokens = self._get_completion(text)
            logger.info("Serializing response...")
            resume = self.serializer.to_json_resume(resume_obj)
        except Exception as e:
            logger.error(f"Error encountered while parsing OpenAI response: {e}")
            resume = {}
            prompt_tokens = 0
            completion_tokens = 0
        t2 = time.time()
        generation_time = t2 - t1
        return resume, prompt_tokens, completion_tokens, generation_time

    def _get_completion(self, text):
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the resume information."},
                    {"role": "user", "content": text},
                ],
                response_format=Resume,
            )

            resume_obj = completion.choices[0].message.parsed
            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
            logger.info(f"OpenAI-Usage => prompt_tokens: {prompt_tokens}  completion_tokens: {completion_tokens}")
            return resume_obj, prompt_tokens, completion_tokens
        except Exception as e:
            logger.error(f"StructuredOutputs Exception: {e}")
            return None, 0, 0
