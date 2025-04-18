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
}


def parse_json(json_output: str):
    # Parsing out the markdown fencing
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(
                lines[i + 1:]
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


def gemini_spatial_understanding(image) -> dict:
    """github/google-gemini/cookbook/Spatial_understanding.ipynb"""
    safety_settings = [
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_ONLY_HIGH",
        ),
    ]

    # Load and resize image
    im = Image.open(BytesIO(open(image, "rb").read()))
    im.thumbnail([1024, 1024], Image.Resampling.LANCZOS)

    # Run model to find bounding boxes
    response = client.models.generate_content(
        model=config["GEMINI_PRO_MODEL"],
        contents=["Here is the screenshot: ", im],
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
        return {
            "status": "error",
            "message": f"""Failed to parse bounding boxes JSON: {e}.
            Raw output: {string}""",
        }

    return bounding_boxes


def analyze_screen():
    """Take a screenshot of the display and store it to the local directory.
    Important:
        To view the screenshot, you must load the image.

    Returns:
        dict: The outcome of the screenshot process, either "ok" or "error".
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

        bounding_boxes = gemini_spatial_understanding(screenshot_path)

        plot_bounding_boxes(screenshot_path, bounding_boxes)

        bounding_boxes = convert_coordinates(bounding_boxes, 1024, 1024)

        print(bounding_boxes)

        if bounding_boxes:
            return {"status": "ok", "bounding_boxes": bounding_boxes}
        else:
            return {"status": "ok"}

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


def convert_coordinates(
    bounding_boxes: list[dict], width: int, height: int
) -> list[dict]:
    """Convert the bounding boxes to clickable coordinates."""
    # Output the positions in [y1 x1 y2 x2] format.
    print(width, height)
    for bounding_box in bounding_boxes:
        print(bounding_box)
        x0 = bounding_box["box_2d"][1]
        x1 = bounding_box["box_2d"][3]
        x0_converted = int(x0 / width * config["MIRRORING_X_BOUND"])
        x1_converted = int(x1 / width * config["MIRRORING_X_BOUND"])
        x_center = int((x0_converted + x1_converted) / 2)

        y0 = bounding_box["box_2d"][0]
        y1 = bounding_box["box_2d"][2]
        y0_inverted = height - y0
        y1_inverted = height - y1
        y0_converted = int(y0_inverted / height * config["MIRRORING_Y_BOUND"])
        y1_converted = int(y1_inverted / height * config["MIRRORING_Y_BOUND"])
        y_center = int((y0_converted + y1_converted) / 2)

        bounding_box["x"] = x_center
        bounding_box["y"] = y_center
        print(bounding_box)
        # Drop the box_2d key
        bounding_box.pop("box_2d")

    return bounding_boxes


def load_screenshot(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Before model callback that automatically loads the screenshot."""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts:
            if (
                llm_request.contents[-1].parts[0].function_response
                and llm_request.contents[-1].parts[0].function_response.name
                == "analyze_screen"
            ):
                screenshot_path = config["SCREENSHOT_LOCATION"].replace(".png", "")
                screenshot_path += "_analyzed.png"

                if os.path.exists(screenshot_path):
                    screenshot_image = Image.open(screenshot_path)

                    with io.BytesIO() as output:
                        screenshot_image.save(output, format="PNG")
                        screenshot_bytes = output.getvalue()

                    screenshot_content = types.Content(
                        parts=[
                            types.Part.from_bytes(
                                data=screenshot_bytes, mime_type="image/png"
                            )
                        ],
                        role="user",
                    )

                    llm_response = LlmResponse(
                        content=screenshot_content,
                    )
                    return llm_response
    pass


if __name__ == "__main__":
    print(analyze_screen())
