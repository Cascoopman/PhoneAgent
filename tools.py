from functools import wraps
from google.genai import types

def model_function_declaration(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Create the function declaration dynamically based on the function's signature
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    # Extract function docstring and parameter types
    docstring = func.__doc__.strip().splitlines()
    param_lines = [line for line in docstring if line.startswith("Args:") or line.startswith("Returns:")]
    
    for line in param_lines:
        if line.startswith("Args:"):
            args_info = line.split(":")[1].strip().split(", ")
            for arg in args_info:
                name, desc = arg.split(":")
                name = name.strip()
                desc = desc.strip()
                parameters["properties"][name] = {
                    "type": "string" if "str" in desc else "integer",
                    "description": desc
                }
                parameters["required"].append(name)

    # Register the function declaration with the model
    function_declaration = {
        "name": func.__name__,
        "description": docstring[0],
        "parameters": parameters,
    }
    
    types.FunctionCall.register(function_declaration)

    return wrapper

@model_function_declaration
def set_light_values(brightness: int, color_temp: str) -> dict[str, int | str]:
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {"brightness": brightness, "colorTemperature": color_temp}






def click_screen(x: int, y: int):
    subprocess.run(["touch", "/tmp/touch.txt"], check=True, capture_output=True, text=True)
    return f"Clicked on the screen at x: {x}, y: {y} successfully."


def swipe_screen(x: int, y: int, direction: str, distance: int):
    subprocess.run(["touch", "/tmp/swipe.txt"], check=True, capture_output=True, text=True)
    return f"Swiped on the screen at x: {x}, y: {y} in the {direction} direction for {distance} pixels successfully."


def home_screen():
    subprocess.run(["touch", "/tmp/home.txt"], check=True, capture_output=True, text=True)
    return "Home screen opened successfully."

def take_screenshot():
    agent.get_history().append(
    types.Content(
        parts=[
            types.Image(
                file_uri=take_screenshot(),
                mime_type="image/png",
            )
        ]
    )
)
