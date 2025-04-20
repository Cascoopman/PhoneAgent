import os

import jinja2
from dotenv import load_dotenv
from google.adk.agents import Agent

from phone_agent.tools.navigation import (
    click_pointer,
    enter_keys,
    home_screen,
    move_pointer,
    scroll_screen,
)
from phone_agent.tools.vision import (
    _load_screenshot,
    get_UI_bounding_boxes,
    take_screenshot,
)

load_dotenv()

# Load prompt from Jinja template
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=jinja2.select_autoescape(),
)
template = env.get_template("prompts/agent.j2")
PROMPT_TEXT = (
    template.render()
)  # https://cookbook.openai.com/examples/gpt4-1_prompting_guide

root_agent = Agent(
    name="phone_agent",
    model=os.getenv("GEMINI_FLASH_MODEL"),
    description="Agent that controls the user's mobile device.",
    instruction=PROMPT_TEXT,  # TODO: Remove implicit instructions.
    tools=[
        home_screen,
        move_pointer,
        click_pointer,
        scroll_screen,
        enter_keys,
        take_screenshot,
        get_UI_bounding_boxes,
    ],
    before_model_callback=_load_screenshot,
)
