import logging
import os
import time
from logging import handlers

from openai import OpenAI


from resume_json.data_model import Resume, ResumeSerializer
from validation import Validation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create file handler that logs debug and higher level messages
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
sh.setFormatter(formatter)

file_logger = bool(os.environ.get("FILE_LOGGER", False))
if file_logger:
    os.makedirs("LOGS", exist_ok=True)
    # Set up file handler
    LOGFILE = "LOGS/resume_parser.log"
    fh = handlers.RotatingFileHandler(LOGFILE, maxBytes=100000, backupCount=10)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
logger.addHandler(sh)

logger.info(f"file_logger value: {file_logger}")


class Parser:
    OPENAI_PARSER_NAME = "openai"
    MODEL_NAME = "gpt-4o-2024-08-06"

    def __init__(self):
        self.validate = Validation()
        self.model = self.MODEL_NAME
        openai_key = os.environ.get("OPENAI_API_KEY", None)
        if not openai_key:
            logger.error("API_KEY_NOT_DEFINED: OpenAI API key is not defined as an environment variable")
        self.client = OpenAI(api_key=openai_key)
        self.serializer = ResumeSerializer()

    def parse(self, text):
        logger.info("Calling OpenAI parser...")
        resume, prompt_tokens, completion_tokens, generation_time = self._query_openai(text)
        num_tokens = prompt_tokens + completion_tokens
        num_chars = len(text)

        valid_json, valid_json_resume = self.validate.validate_json(resume)
        logger.info(
            f"parser: {self.OPENAI_PARSER_NAME}, valid_json: {valid_json}, valid_jsonresume: {valid_json_resume}, num_chars: {num_chars}, num_tokens: {num_tokens}, generation_time: {generation_time} ")

        return {
            "parser": self.OPENAI_PARSER_NAME,
            "is_valid_json": valid_json,
            "is_valid_jsonresume": valid_json_resume,
            "generation_time": generation_time,
            "num_chars": num_chars,
            "num_tokens": num_tokens,
            "jsonresume": resume,

        }

    def parse_standalone(self, text):
        response = self.parse(text)
        return response

    def _query_openai(self, text):
        t1 = time.time()
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
            logger.info(f"prompt_tokens: {prompt_tokens}  completion_tokens: {completion_tokens}")
            resume = self.serializer.to_json_resume(resume_obj)
        except:
            logger.error("Error encountered while parsing OpenAI response")
            resume = {}
            prompt_tokens = 0
            completion_tokens = 0
        t2 = time.time()
        generation_time = t2 - t1
        return resume, prompt_tokens, completion_tokens, generation_time
