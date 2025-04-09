import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool

from .prompt import PROMPT
from .tools import click_screen, finish, swipe_screen, take_screenshot

load_dotenv()

root_agent = Agent(
    name="passpilot_agent",
    model=os.getenv("GEMINI_MODEL"),
    description="Reset password agent.",
    instruction=PROMPT,
    tools=[click_screen, swipe_screen, take_screenshot, load_artifacts_tool, finish],
)
