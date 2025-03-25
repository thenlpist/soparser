import json
import logging
import os
from json import JSONDecodeError
from logging import handlers
from pathlib import Path

from resume_json.data_model import Resume

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create file handler that logs debug and higher level messages
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s")
sh.setFormatter(formatter)

file_logger = bool(os.environ.get("FILE_LOGGER", False))
if file_logger:
    # Set up file handler
    LOGFILE = "LOGS/resume_parser.log"
    fh = handlers.RotatingFileHandler(LOGFILE, maxBytes=100000, backupCount=10)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
logger.addHandler(sh)


class Validation:
    app_dir = Path(__file__).parent.resolve()

    def validate_json(self, obj):
        valid_json = False
        valid_json_resume = False

        d = None

        if isinstance(obj, dict):
            valid_json = True
            d = obj
        else:
            try:
                d = json.loads(obj)
                valid_json = True
            except (JSONDecodeError, TypeError) as e:
                logger.error(f"JSONValidationError: invalid json for generated object: {obj}")

        if d:
            try:
                resume_obj = Resume.model_validate(d)
                valid_json_resume = True
            except:
                logger.error("Response object can not be deserialized to a Resume Pydantic object")

        return valid_json, valid_json_resume
