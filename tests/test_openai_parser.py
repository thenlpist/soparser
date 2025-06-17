import json
import os
import unittest
from pathlib import Path
from dotenv import load_dotenv
from nlptk import FileReader
from nlptk import PostProcess
from rtk import OAiParser

class TestOpenAIParser(unittest.TestCase):
    cwd = Path.cwd()
    resources_dir = cwd.joinpath("resources")
    load_dotenv()
    openai_api_key = os.getenv("PROD_OPENAI_API_KEY")
    pp = PostProcess()


    def test_resume1(self):
        resume_path = self.resources_dir.joinpath("resumes/Ethan.docx")
        # resume_path = resources_dir.joinpath("resumes/Genevieve.pdf")

        assert resume_path.exists()
        reader = FileReader()
        text = reader.extract_text(resume_path)
        fallback = OAiParser(self.openai_api_key)
        response = fallback.parse(text)

        verbose = True
        if verbose:
            print("Response:")
            print(f"type(response):  {type(response)}")
            print(json.dumps(response, indent=2))


        jsonresume = response.get("jsonresume")
        jsonresume, is_valid_json, is_valid_jsonresume = self.pp.postprocess(jsonresume)
        print(f"is_valid_json:         {is_valid_json}")
        print(f"is_valid_jsonresume:   {is_valid_jsonresume}")



    def test_resume2(self):


        resume_path = resources_dir.joinpath("resumes/Ethan.docx")
        # resume_path = resources_dir.joinpath("resumes/Genevieve.pdf")

        assert resume_path.exists()
        reader = FileReader()
        text = reader.extract_text(resume_path)
        fallback = OAiParser(self.openai_api_key)
        response = fallback.parse(text)

        verbose = True
        if verbose:
            print("Response:")
            print(f"type(response):  {type(response)}")
            print(json.dumps(response, indent=2))


        jsonresume = response.get("jsonresume")
        jsonresume, is_valid_json, is_valid_jsonresume = self.pp.postprocess(jsonresume)
        print(f"is_valid_json:         {is_valid_json}")
        print(f"is_valid_jsonresume:   {is_valid_jsonresume}")


if __name__ == "__main__":
    unittest.main()
