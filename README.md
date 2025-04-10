# Readme
Use LLM API to parse unstructured data using Structured Outputs


## Build Instructions

Generate a distribution package
(1) make sure you have the latest version of PyPA build installed
```
python -m pip install --upgrade build
```

(2) then build
```
python -m build
```

This will generate two files in the `dist` directory


## Install local instructions

You can install locally by pointing pip at the dist folder
e.g. 
```
 pip install dist/rtk-0.1.0-py3-none-any.whl
```


## How to use

import

```python
# from rtk.openai_parser import Parser
from rtk import OAiParser
text = "..."
parser = OAiParser()
parser.parse_standalone(text)
```

