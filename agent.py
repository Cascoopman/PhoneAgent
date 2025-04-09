from google import genai
from google.genai import types
from google.genai.types import ContentOrDict, Content, ContentDict
from pydantic import BaseModel

import yaml
import os
from dotenv import load_dotenv
from tools import click_screen, swipe_screen, take_screenshot

load_dotenv()


class ScreenshotAnalysis(BaseModel):
    reasoning: str
    decision: str

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

class PassPilot():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PassPilot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=os.getenv("GCP_PROJECT_ID"),
            location=config["GCP_LOCATION"],
        )

    def start_agent(self):
        self.agent = self.client.aio.chats.create(
            model=config["GEMINI_MODEL"],
            config=types.GenerateContentConfig(
                response_schema=ScreenshotAnalysis,
                tools=[click_screen, swipe_screen],
            ),
        )

    def create_response(self, image_path):
        response = self.agent.send_message(
            message=types.Content(
                parts=[
                    types.Image(
                        file_uri=image_path,
                        mime_type="image/png",
                    )
                ]
            ),
            config=types.GenerateContentConfig(
                response_schema=ScreenshotAnalysis,
                tools=[click_screen, swipe_screen],
            ),
        )

    def get_response(self):
        return self.agent.get_history()
