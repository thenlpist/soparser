import importlib.metadata
import random
from typing import Optional
import logging
import os
import time

from openai import OpenAI

from rtk.resume_dataclass import Resume, ResumeSerializer
from rtk.validation import Validation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler that logs debug and higher level messages
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)


class OAiParser:
    OPENAI_PARSER_NAME = "openai"
    OPENAI_FAIL_NAME = "openai-error"

    def __init__(self, openai_key, config: Optional[dict]):
        self.config = config
        flags = {(f["name"]): {"enabled": f["enabled"], "environment": f.get("environment", None) } for f in config["flags"]}
        logger.debug(f"flags: {flags}")
        experiment = flags.get("experiment", {})
        logger.debug(f"experiment: {experiment}")
        current_env = config.get("current_env", "")
        logger.debug(f"current_env: {current_env}")
        if not experiment:
            self.test = False
        else:
            enabled = experiment.get("enabled", False)
            environment = experiment.get("environment", None)
            logger.debug(f"experiment enabled: {enabled}, environment: {environment}   current env: {current_env}")
            if enabled and environment == current_env:
                self.test = True
            else:
                self.test = False

        logger.info(f"(OAiParser) config.test: {self.test}")
        self.validate = Validation()
        self.model = "gpt-4o-2024-08-06"
        openai_key = openai_key if openai_key else os.environ.get("OPENAI_API_KEY", None)
        self.openai_is_available = True
        if not openai_key:
            logger.error("(OAiParser) OpenAI API key is not defined as an environment variable")
            self.openai_is_available = False
        self.client = OpenAI(api_key=openai_key)
        self.serializer = ResumeSerializer()
        self.var = ""
        self.version_string = importlib.metadata.version("rtk")

    def parse(self, text):
        valid_key = self._validate_key()
        if not valid_key:
            return {"parser": self.OPENAI_FAIL_NAME,
                    "is_valid_json": False,
                    "is_valid_jsonresume": False,
                    "jsonresume": {}}
        head = text[:100].replace("\n", " ")
        logger.info(f"(OAiParser) Calling OpenAI parser for text: {head}...")
        resume, prompt_tokens, completion_tokens, generation_time = self._query_openai(text)
        num_tokens = prompt_tokens + completion_tokens
        num_chars = len(text)
        # logger.debug("Validating returned object...")
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
            "jsonresume": resume,
            "sop": f"{self.version_string}{self.var}"
        }

    def parse_standalone(self, text):
        text, var = self._perturb_text(text)
        response = self.parse(text)
        response, statuscode = self.validate.compute_statuscode(response)
        response["statuscode"] = statuscode
        response["var"] = var
        return response

    def _perturb_text(self, text):
        var = ""
        if self.test:
            time.sleep(3)
            if random.random() < 0.3:
                offsets = [2000, 3000, 4000]
                offset = random.choice(offsets)
                var = f"p1-{offset}"
                text = text[:offset]
            elif random.random() < 0.3:
                var = "p2"
                lines = text.split("\n")
                num_lines = len(lines)
                offset = min(20, int(num_lines / 4))
                var = f"p2-{offset}"
                start = lines[:offset]
                end = lines[offset:]
                random.shuffle(end)
                new_items = start + end
                text = "\n".join(new_items)
            elif random.random() < 0.3:
                var = "p3"
                text = text[300:].replace("\n", " ")
            else:
                var = "n"
            logger.debug(f"(OAiParser) perturbation: {var}")
        self.var = f".{var}" if var else ""
        return text, var


    def _validate_key(self):
        if self.openai_is_available == False:
            logger.error("(OAiParser) OpenAI Key is not defined")
            return False
        return True

    def _query_openai(self, text):
        t1 = time.time()
        try:
            resume_obj, prompt_tokens, completion_tokens = self._get_completion(text)
            logger.debug("(OAiParser) Serializing response...")
            resume = self.serializer.to_json_resume(resume_obj)
        except Exception as e:
            logger.error(f"(OAiParser) Error encountered while parsing OpenAI response: {e}")
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
            logger.info(f"(OAiParser) OpenAI-Usage => prompt_tokens: {prompt_tokens}  completion_tokens: {completion_tokens}")
            return resume_obj, prompt_tokens, completion_tokens
        except Exception as e:
            logger.error(f"(OAiParser) StructuredOutputs Exception: {e}")
            return None, 0, 0
