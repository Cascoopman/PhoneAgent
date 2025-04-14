import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool

from .prompt import PROMPT
from .tools import (
    click_pointer,
    enter_keys,
    finish,
    home_screen,
    move_pointer_from_current_to,
    move_pointer_to_position,
    swipe_screen,
    take_screenshot,
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
        swipe_screen,
        enter_keys,
        take_screenshot,
        load_artifacts_tool,
        home_screen,
        finish,
    ],
)
