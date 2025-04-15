from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

from passpilot_agent.tools.vision.vision import load_screenshot


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    llm_response = load_screenshot(callback_context, llm_request)
    if llm_response:
        return llm_response
    return None
