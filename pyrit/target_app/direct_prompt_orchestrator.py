import textwrap
import asyncio
from pathlib import Path
import json

from pyrit.common import IN_MEMORY, initialize_pyrit
from pyrit.orchestrator import PromptSendingOrchestrator, RedTeamingOrchestrator, CrescendoOrchestrator, PAIROrchestrator
from pyrit.prompt_converter import SearchReplaceConverter, SuffixAppendConverter, AsciiSmugglerConverter, AsciiArtConverter
from pyrit.score import SelfAskTrueFalseScorer, TrueFalseInverterScorer, PromptShieldScorer, TrueFalseQuestion, AzureContentFilterScorer
from pyrit.prompt_target import (
    HTTPTarget,
    OpenAIChatTarget,
    get_http_target_json_response_callback_function,
    get_http_target_regex_matching_callback_function,
)
import logging
from random import randint
import os
import secrets
import string
import yaml
from dotenv import load_dotenv

from target_app.helper import parse_target_json_http_response, get_target_http_request, TargetSuffixAppendConverter


SCRIPT_CWD = Path(__file__).parent.resolve()
# DEFAULT_PROMPT_COLLECTION = os.environ.get("DEFAULT_PROMPT_COLLECTION", SCRIPT_CWD / "direct_prompts.yaml")
DEFAULT_PROMPT_COLLECTION = SCRIPT_CWD / "direct_prompts.yaml"
SELECTED_PROMPT_GROUP = os.environ.get("SELECTED_PROMPT_GROUP", None)

# Load environment variables from credentials.env file
load_dotenv("credentials.env")

async def main():
    """
    Main function to run the PyRIT test.
    Initializes the PyRIT environment and runs a red teaming attack against a Gandalf target.
    """
    print("Running PyRIT test...")
    logging.basicConfig(level=logging.WARNING)

    target_endpoint=os.getenv("TARGET_ENDPOINT")
    target_api_key=os.getenv("TARGET_API_KEY")
    # aoai_endpoint=os.getenv("OPENAI_CHAT_ENDPOINT")
    # aoai_api_key=os.getenv("OPENAI_CHAT_KEY")
    # aoai_api_version=os.getenv("OPENAI_CHAT_API_VERSION", "2025-01-01-preview")
    session_id=os.getenv("TARGET_SESSION_ID", None)

    # Logging set to lower levels will print a lot more diagnostic information about what's happening.
    logging.basicConfig(level=logging.INFO)
    initialize_pyrit(memory_db_type=IN_MEMORY)

    # Load prompts from YAML file
    prompts: dict = {}
    with open(DEFAULT_PROMPT_COLLECTION, "r") as f:
        prompts: dict = yaml.safe_load(f) # type: ignore

    if SELECTED_PROMPT_GROUP is None:
        selected_prompt_group = list(prompts.keys())
    elif SELECTED_PROMPT_GROUP not in prompts:
        print(f"Selected prompt key '{SELECTED_PROMPT_GROUP}' not found in prompts. Using all prompts instead.")
        selected_prompt_group = list(prompts.keys())
    else:
        selected_prompt_group = [SELECTED_PROMPT_GROUP]
    print(f"Iterating over [{",".join(selected_prompt_group)}] prompts from: {DEFAULT_PROMPT_COLLECTION}")

    for pg in selected_prompt_group:
        # Raw target HTTP Request example:
        if session_id is None:
            session_id = f"us_{secrets.token_hex(4)}"
            print("Generated session and user id:", session_id)
        target_http_request = get_target_http_request(
            target_endpoint=target_endpoint,
            target_api_key=target_api_key,
            user_id=session_id,
            session_id=session_id
        )

        print(f"Http Request:\n{target_http_request}")
        http_prompt_target = HTTPTarget(
            http_request=target_http_request, prompt_regex_string="{PROMPT}",
            timeout=60,
            callback_function=parse_target_json_http_response,
        )

        print(f"Running prompt id: {pg}")
        suffix = prompts[pg]["suffix"]
        prompt_list = prompts[pg]["prompts"]
        suffix_converter = TargetSuffixAppendConverter(suffix=suffix, separator="")
        orchestrator = PromptSendingOrchestrator(objective_target=http_prompt_target, prompt_converters=[suffix_converter])
        for prompt in prompt_list:
            print(f"Sending prompt: {prompt}")
            await orchestrator.send_prompts_async(prompt_list=prompt_list)  # type: ignore
        await orchestrator.print_conversations_async()  # type: ignore


if __name__ == '__main__':
    asyncio.run(main())
