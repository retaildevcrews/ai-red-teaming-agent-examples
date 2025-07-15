import secrets
import string
import json

from pyrit.models import PromptDataType
from pyrit.prompt_converter import ConverterResult, SuffixAppendConverter


class TargetSuffixAppendConverter(SuffixAppendConverter):

    def __init__(self, *, separator=" ", suffix: str):
        if not suffix:
            raise ValueError("Please specify a suffix (str) to be appended to the prompt.")

        self.suffix = suffix
        self.separator = separator

    async def convert_async(self, *, prompt: str, input_type: PromptDataType = "text") -> ConverterResult:
        """
        Simple converter that appends a given suffix to the prompt.
        E.g. with a suffix `!!!`, it converts a prompt of `test` to `test !!!`

        See PyRIT/pyrit/auxiliary_attacks/gcg for adversarial suffix generation

        Args:
            prompt (str): The prompt to be converted.

        Returns:
            list[str]: The converted prompts.
        """
        if not self.input_supported(input_type):
            raise ValueError("Input type not supported")

        return ConverterResult(output_text=prompt + self.separator + self.suffix, output_type="text")

    def input_supported(self, input_type: PromptDataType) -> bool:
        return input_type == "text"

    def output_supported(self, output_type: PromptDataType) -> bool:
        return output_type == "text"

def get_target_http_request(target_endpoint: str|None, target_api_key: str|None, user_id: str|None = None, session_id: None|str = None) -> str:
    """Generates a raw HTTP request string for the Target API.
    Returns:
        str: A formatted HTTP request string with placeholders for the prompt.
    """

    if target_endpoint is None or target_api_key is None:
        raise ValueError("Both target_endpoint and target_api_key must be provided.")

    # Generate random user_id and session_id if not provided
    user_id = f"pyrit_auto_u_{secrets.token_hex(8)}" if user_id is None else user_id
    session_id = f"pyrit_auto_s_{secrets.token_hex(8)}" if session_id is None else session_id
    # user_id = session_id= randint(10000, 99999)
    # Raw HTTP Request example:
    return f"""
        POST {target_endpoint} HTTP/1.1
        Content-Type: application/json
        Ocp-Apim-Subscription-Key: {target_api_key}

        {{
            "input": {{
                "question": "{{PROMPT}}"
            }},
            "config": {{
                "configurable": {{
                    "session_id": "{session_id}",
                    "user_id": "{user_id}"
                }}
            }}
        }}
    """


def parse_target_json_http_response(response):
    """
    Purpose: parses json outputs and makes it nicer for LLMs to read.
    Parameters:
        response (response): the HTTP Response to parse
    Returns: parsed output from response given by the Target API in plain text format.
    """
    json_response = json.loads(response.content)

    try:
        if "output" in json_response and json_response["output"] != "":
            response_to_adversarial_chat = json_response["output"]
            if "displayResponse" in response_to_adversarial_chat:
                return response_to_adversarial_chat["displayResponse"]
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Returning full response:")
    return json_response
