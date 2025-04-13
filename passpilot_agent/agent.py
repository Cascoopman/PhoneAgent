import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool

from .prompt import PROMPT
from .tools import (
    enter_keys,
    swipe_left,
    swipe_right,
    swipe_up,
    swipe_down,
    move_pointer_to_position,
    move_pointer_from_current_to,
    click_pointer,
    take_screenshot,
    home_screen,
    finish,
)

load_dotenv()

root_agent = Agent(
    name="passpilot_agent",
    model=os.getenv("GEMINI_MODEL"),
    description="Reset password agent.",
    instruction=PROMPT,
    tools=[
        move_pointer_to_position,
        move_pointer_from_current_to,
        click_pointer,
        swipe_left,
        swipe_right,
        swipe_up,
        swipe_down,
        enter_keys,
        take_screenshot,  # TODO: move vision logic to separate agent?
        load_artifacts_tool,
        home_screen,
        finish,
    ],
)
