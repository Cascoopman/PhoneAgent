import io
import os
import subprocess
import sys
from datetime import datetime
from typing import Callable

import pyautogui
from dotenv import load_dotenv
from google.adk.tools import ToolContext
from google.genai import types
from PIL import Image
from pydantic import BaseModel

load_dotenv()

config = {
    "SCREENSHOT_DIR": os.getenv("SCREENSHOT_DIR"),
    "SCREEN_Y_BOUND": int(os.getenv("SCREEN_Y_BOUND")),
    "SCREEN_X_BOUND": int(os.getenv("SCREEN_X_BOUND")),
}

class Callback(BaseModel):
    before_model_callback: Callable
    after_model_callback: Callable
    before_agent_callback: Callable
    after_agent_callback: Callable

class Tool(BaseModel):
    before_tool_callback: Callable
    tool_function: Callable
    after_tool_callback: Callable

    def before_model_callback(
        self, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        pass

class ToolContext(BaseModel):
    tools: List[Tool]

    def get_tools(self) -> List[Tool]:
        return self.tools

    def get_tool_by_name(self, name: str) -> Tool:
        for tool in self.tools:
            if tool.name == name:
                return tool

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

def click_screen(x: int, y: int) -> dict:
    """
    This tool is used to click on the screen at the given coordinates.

    Args:
        x (int): The x coordinate to click on.
        y (int): The y coordinate to click on.
    """
    if y > config["SCREEN_Y_BOUND"] or x > config["SCREEN_X_BOUND"]:
        return {
            "status": "error",
            "message": (
                "Invalid coordinates. "
                "Please provide coordinates within the screen bounds. "
                f"Screen bounds are {config['SCREEN_X_BOUND']}x{config['SCREEN_Y_BOUND']}."
            ),
        }

    y = config["SCREEN_Y_BOUND"] - y
    pyautogui.click(x, y)
    return {"status": "ok"}


def swipe_screen(x_offset: int, y_offset: int) -> dict:
    """
    Performs a mouse drag relative from its current position.

    Args:
        x_offset (int): The x offset to drag to.
        y_offset (int): The y offset to drag to.
    """
    y_offset = -y_offset
    pyautogui.drag(x_offset, y_offset, button="left")
    return {"status": "ok"}


def take_screenshot(tool_context: ToolContext) -> dict:
    """
    This tool is used to take a screenshot of the iPhone display and stores it
    as an image artifact.

    Returns:
        dict: A dictionary containing the status and the filename of
        the saved screenshot artifact.
    """
    # Ensure the screenshot directory exists
    os.makedirs(config["SCREENSHOT_DIR"], exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(config["SCREENSHOT_DIR"], f"{timestamp}.png")

    try:
        # Use shell=True carefully, ensure command is safe
        # On macOS, screencapture is a safe, standard utility
        subprocess.run(
            ["screencapture", screenshot_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Screen capture successful.")

        # Open the captured image
        with Image.open(screenshot_path) as img:
            width, height = img.size
            # Define the box for the left quarter
            # (left, upper, right, lower)
            left_quarter_box = (0, (height // 4), width // 4, height)
            # Crop the image
            cropped_img = img.crop(left_quarter_box)

            # Turn Image into ImageFile and save artifact
            image_file = io.BytesIO()
            cropped_img.save(image_file, format="PNG")
            image_file.seek(0)  # Go to the beginning of the stream
            img_byte_arr = image_file.getvalue()

            tool_context.save_artifact(
                screenshot_path,
                types.Part.from_bytes(data=img_byte_arr, mime_type="image/png"),
            )

        return {"status": "ok", "filename": screenshot_path}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error capturing screen: {str(e)}"}
    except FileNotFoundError:
        # print("Error: 'screencapture' command not found. Ensure you are on macOS.")
        return {
            "status": "error",
            "message": (
                "Error: 'screencapture' command not found. Ensure you are on macOS."
            ),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred during image processing: {e}",
        }


def finish():
    """
    This tool is used to stop the process.
    """
    sys.exit(0)


if __name__ == "__main__":
    click_screen(100, 100)
    swipe_screen(100, 100)
