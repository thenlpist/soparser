import os
import unittest

from dotenv import load_dotenv
from nlptk import PostProcess
from openai import OpenAI


class TestOpenAIParser(unittest.TestCase):
    load_dotenv()
    openai_api_key = os.getenv("PROD_OPENAI_API_KEY")
    pp = PostProcess()

    def test_resume(self):
        client = OpenAI(api_key=self.openai_api_key)

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ]
        )
        print(chat_completion.choices[0].message.content)
        assert chat_completion.choices[0].message.content != None


if __name__ == "__main__":
    unittest.main()
