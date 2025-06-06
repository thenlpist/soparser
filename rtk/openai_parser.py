import json
import logging
import os
import time
from pathlib import Path

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

# file_logger = bool(os.environ.get("FILE_LOGGER", False))
# if fFILE_LOGGERile_logger:
#     os.makedirs("LOGS", exist_ok=True)
#     # Set up file handler
#     LOGFILE = "LOGS/resume_parser.log"
#     fh = handlers.RotatingFileHandler(LOGFILE, maxBytes=100000, backupCount=10)
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)
logger.addHandler(sh)


# logger.info(f"rtk file_logger value: {file_logger}")


class OAiParser:
    OPENAI_PARSER_NAME = "openai"

    def __init__(self, openai_key):
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
        if self.openai_is_available == False:
            logger.error("OpenAI is unavailable")
            return {"parser": "None", "jsonresume": {}}
        logger.info("Calling OpenAI parser...")
        resume, prompt_tokens, completion_tokens, generation_time = self._query_openai(text)
        num_tokens = prompt_tokens + completion_tokens
        num_chars = len(text)

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
        response = self.parse(text)
        response, statuscode = self.validate.compute_statuscode(response)
        response["statuscode"] = statuscode
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


def main(text):
    parser = OAiParser()
    response = parser.parse_standalone(text)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    home = Path.home()
    data_dir = home.joinpath("Data/Jobscan/Resumes/2_Annotation/20250326_Resume_labeling/Resumes_to_label")
    # text = open(data_dir.joinpath("4587062.txt")).read()
    text = open(data_dir.joinpath("4590187.txt")).read()
    main(text)
