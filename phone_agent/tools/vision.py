import io
import json
import os
import subprocess  # nosec
from io import BytesIO
from typing import Optional

import jinja2
from dotenv import load_dotenv
from google import genai
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types
from PIL import Image, ImageColor, ImageDraw

load_dotenv()

client = genai.Client(vertexai=True)

additional_colors = [colorname for (colorname, _) in ImageColor.colormap.items()]

config = {
    "SCREENSHOT_LOCATION": os.getenv("SCREENSHOT_LOCATION"),
    "GEMINI_PRO_MODEL": os.getenv("GEMINI_PRO_MODEL"),
    "IMAGE_CROP_BOX": tuple(map(int, os.getenv("IMAGE_CROP_BOX").split(","))),
    "MIRRORING_X_BOUND": int(os.getenv("MIRRORING_X_BOUND")),
    "MIRRORING_Y_BOUND": int(os.getenv("MIRRORING_Y_BOUND")),
    "SCREEN_Y_INVERSION": int(os.getenv("SCREEN_Y_INVERSION")),
    "CONVERSION_WIDTH": int(os.getenv("CONVERSION_WIDTH")),
    "CONVERSION_HEIGHT": int(os.getenv("CONVERSION_HEIGHT")),
}

os.makedirs(os.path.dirname(config["SCREENSHOT_LOCATION"]), exist_ok=True)


def parse_json(json_output: str):
    # Parsing out the markdown fencing
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(
                lines[i + 1 :]
            )  # Remove everything before "```json"
            json_output = json_output.split("```")[
                0
            ]  # Remove everything after the closing "```"
            break  # Exit the loop once "```json" is found
    return json_output


def plot_bounding_boxes(im, bounding_boxes):
    """
    Plots bounding boxes on an image with markers for each a name, using PIL,
    normalized coordinates, and different colors.

    Args:
        img_path: The path to the image file.
        bounding_boxes: A list of bounding boxes containing the name of the object
         and their positions in normalized [y1 x1 y2 x2] format.
    """

    # Load the image
    img = Image.open(BytesIO(open(im, "rb").read()))

    width, height = img.size

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    # Define a list of colors
    colors = [
        "red",
        "green",
        "blue",
        "yellow",
        "orange",
        "pink",
        "purple",
        "brown",
        "gray",
        "beige",
        "turquoise",
        "cyan",
        "magenta",
        "lime",
        "navy",
        "maroon",
        "teal",
        "olive",
        "coral",
        "lavender",
        "violet",
        "gold",
        "silver",
    ] + additional_colors

    # font = ImageFont.truetype("NotoSansCJK-Regular.ttc", size=14)

    # Iterate over the bounding boxes
    for i, bounding_box in enumerate(bounding_boxes):
        # Select a color from the list
        color = colors[i % len(colors)]

        # Convert normalized coordinates to absolute coordinates
        abs_y1 = int(bounding_box["box_2d"][0] / 1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1] / 1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2] / 1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3] / 1000 * width)

        if abs_x1 > abs_x2:
            abs_x1, abs_x2 = abs_x2, abs_x1

        if abs_y1 > abs_y2:
            abs_y1, abs_y2 = abs_y2, abs_y1

        # Draw the bounding box
        draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=4)

        # Draw the text
        if "label" in bounding_box:
            draw.text((abs_x1 + 8, abs_y1 + 6), bounding_box["label"], fill=color)

    # Display the image
    img.save(im.replace(".png", "_analyzed.png"))


def get_instructions() -> str:
    # Point the loader to the parent directory containing the 'prompts' folder
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(prompts_dir),
        autoescape=jinja2.select_autoescape(),
    )
    # Load the template directly by its name within the prompts directory
    template = env.get_template("vision.j2")
    return template.render()


def gemini_spatial_understanding(image, query) -> list[dict]:
    """github/google-gemini/cookbook/Spatial_understanding.ipynb"""
    safety_settings = [
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_ONLY_HIGH",
        ),
    ]

    # Load and resize image
    im = Image.open(BytesIO(open(image, "rb").read()))
    im.thumbnail(
        [config["CONVERSION_WIDTH"], config["CONVERSION_HEIGHT"]],
        Image.Resampling.LANCZOS,
    )

    # Run model to find bounding boxes
    response = client.models.generate_content(
        model=config["GEMINI_PRO_MODEL"],
        contents=[
            "Here is what you should focus on: " + query,
            im,
        ],
        config=types.GenerateContentConfig(
            system_instruction=get_instructions(),
            temperature=0.5,
            safety_settings=safety_settings,
        ),
    )

    string = parse_json(response.text)

    try:
        bounding_boxes = json.loads(string)
    except json.JSONDecodeError as e:
        return [
            {
                "status": "error",
                "message": f"""Failed to parse bounding boxes JSON: {e}.
            Raw output: {string}""",
            }
        ]

    try:
        bounding_boxes[0]["box_2d"]
    except KeyError:
        return [
            {
                "status": "error",
                "message": f"No bounding boxes found. Raw response: {string}",
            }
        ]

    return bounding_boxes


def take_screenshot(explanation: str) -> dict:
    """
    Captures a screenshot of the current iPhone screen and returns it as image
    data. This is crucial for verifying the current UI state before planning
    actions.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.

    Returns:
        dict: The outcome of the screenshot process.
    """
    os.makedirs(os.path.dirname(config["SCREENSHOT_LOCATION"]), exist_ok=True)
    screenshot_path = config["SCREENSHOT_LOCATION"]
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    try:
        subprocess.run(  # nosec
            ["screencapture", "-C", screenshot_path],
            check=True,
            capture_output=True,
            text=True,
        )

        # Crop the image using PIL
        with Image.open(screenshot_path) as img:
            left_quarter_box = config["IMAGE_CROP_BOX"]
            pil_cropped_img = img.crop(left_quarter_box)
            pil_cropped_img.save(screenshot_path)

        return {"status": "screenshot captured"}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error capturing screen: {str(e)}"}
    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": (
                "Error: 'screencapture' command not found. Ensure you are on macOS. "
                f"Error: {e}"
            ),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred during image processing: {e}",
        }


def locate_UI_elements(explanation: str, query: str) -> dict:
    """
    Analyzes the latest screenshot to locate specific UI elements described by
    the query. Returns a list of found elements, including their center coordinates
    (x, y). Essential *before* using `move_pointer`. Be specific in your query.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        query (str): A natural language description of the UI element(s) to
          locate (e.g., 'the settings icon', 'the text field labeled username',
          'button containing Send').

    Returns:
        dict: The outcome of the object location process.
    """
    bounding_boxes = gemini_spatial_understanding(config["SCREENSHOT_LOCATION"], query)

    if bounding_boxes[0].get("status", None) and (
        bounding_boxes[0].get("status") == "warning"
        or bounding_boxes[0].get("status") == "error"
    ):
        return bounding_boxes[0]

    plot_bounding_boxes(config["SCREENSHOT_LOCATION"], bounding_boxes)

    bounding_boxes = convert_coordinates(bounding_boxes)

    return {
        "status": "localization process completed",
        "coordinates": bounding_boxes,
    }


def convert_coordinates(bounding_boxes: list[dict]) -> list[dict]:
    """Convert the bounding boxes to clickable coordinates."""
    height, width = 1000, 1000  # Gemini returns coordinates in 1000x1000 pixels
    x_bound, y_bound = config["MIRRORING_X_BOUND"], config["MIRRORING_Y_BOUND"]

    for bounding_box in bounding_boxes:
        x_center = int(
            (
                int(bounding_box["box_2d"][1] / width * x_bound)
                + int(bounding_box["box_2d"][3] / width * x_bound)
            )
            / 2
        )

        y_center = int(
            (
                int((height - bounding_box["box_2d"][0]) / height * y_bound)
                + int((height - bounding_box["box_2d"][2]) / height * y_bound)
            )
            / 2
        )

        bounding_box["x"] = x_center
        bounding_box["y"] = y_center
        bounding_box.pop("box_2d")

    return bounding_boxes


def _load_screenshot(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Before model callback that automatically loads the screenshot."""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts:
            if (
                llm_request.contents[-1].parts[0].function_response
                and llm_request.contents[-1].parts[0].function_response.name
                == "take_screenshot"
            ):
                screenshot_path = config["SCREENSHOT_LOCATION"]
                if os.path.exists(screenshot_path):
                    screenshot_image = Image.open(screenshot_path)

                    with io.BytesIO() as output:
                        screenshot_image.save(output, format="PNG")
                        screenshot_bytes = output.getvalue()

                    llm_request.contents.append(
                        types.Content(
                            parts=[
                                types.Part.from_bytes(
                                    data=screenshot_bytes, mime_type="image/png"
                                )
                            ],
                            role="user",
                        )
                    )

    # -- solves google.genai.errors.ClientError: 400 INVALID_ARGUMENT --
    if llm_request.contents and llm_request.contents[-1].role == "model":
        if llm_request.contents[-1].parts:
            if llm_request.contents[-1].parts[0].text:
                if llm_request.contents[-1].parts[0].text == "":
                    llm_request.contents[-1].parts[0].text = " "
    if (  # looping agent adds a 'user' part at [-1] so we need to check [-2]
        llm_request.contents
        and len(llm_request.contents) > 1
        and llm_request.contents[-2].role == "model"
    ):
        if llm_request.contents[-2].parts:
            if llm_request.contents[-2].parts[0].text:
                if llm_request.contents[-2].parts[0].text == "":
                    llm_request.contents[-2].parts[0].text = " "

    return None


if __name__ == "__main__":
    input = [{"box_2d": [898, 486, 943, 843], "label": "text input field"}]
    print(convert_coordinates(input))

    # outputs 402, 67
