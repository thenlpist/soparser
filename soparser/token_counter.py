import nltk
from transformers import T5Tokenizer


class TokenCounter:

    def __init__(self):
        tokenizer_name = "google-t5/t5-base"
        self.tokenizer = T5Tokenizer.from_pretrained(tokenizer_name, legacy=False)
        # new_words = ["{", "}", "~", "\\", "\n"]
        new_words = ["{", "}", "~"]
        self.tokenizer.add_tokens(new_words)

    def compute_num_tokens(self, text):
        tokenized_data = self.sentencepiece_tokenize(text)
        num_tokens = int(tokenized_data["length"][0])
        return num_tokens

    def sentencepiece_tokenize(self, text):
        tokenized_data = self.tokenizer(text, return_length=True, return_tensors="pt")
        return tokenized_data

    def nltk_tokenize(self, text):
        tokenized_text = nltk.word_tokenize(text)
        num_terms = len(tokenized_text)
        return num_terms

    def inspect(self, text, tokenizer):
        ''' Convenience method for inspecting encoded tokens.
        Useful for discovering what is not in the tokenizer vocabulary.
        '''
        tokenized_data = tokenizer(text, return_length=True, return_tensors="pt")
        input_ids = tokenized_data.input_ids
        [tokenizer.convert_ids_to_tokens([ele]) for ele in input_ids[0]]

# def process(d):
#     text = d["text"]
#     jr = d["resume_json"]
#     tokenized_data1 = sentencepiece_tokenize(text)
#     d["num_tokens_text"] = int(tokenized_data2["length"][0])
#     tokenized_data2 = sentencepiece_tokenize(json.dumps(jr))
#     d["num_tokens_jsonresume"] = int(tokenized_data2["length"][0])
#     return d
#
#
# def sentencepiece_tokenize(text):
#     tokenized_data = tokenizer(text, return_length=True, return_tensors="pt")
#     return tokenized_data
