import os

import jinja2
from dotenv import load_dotenv
from google.adk.agents import Agent

from phone_agent.library.callbacks import before_model_callback
from phone_agent.tools import tools_list

load_dotenv()

# Load prompt from Jinja template
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=jinja2.select_autoescape(),
)
template = env.get_template("prompt.j2")
PROMPT_TEXT = template.render()  # https://cookbook.openai.com/examples/gpt4-1_prompting_guide

root_agent = Agent(
    name="phone_agent",
    model=os.getenv("GEMINI_MODEL"),
    description="Agent that can control the user's mobile device.",
    instruction=PROMPT_TEXT,  # TODO: Remove implicit instructions.
    tools=[
        *tools_list,
    ],
    before_model_callback=before_model_callback,
)
