import math
import os

import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from PIL import Image
from shapely.geometry import box as shapely_box
from ultralytics import YOLO

load_dotenv()

config = {
    "PATH_TO_MODEL": "model/weights.pt",
    "CONFIDENCE_THRESHOLD": float(os.getenv("CONFIDENCE_THRESHOLD", 0.5)),
    "OVERLAP_THRESHOLD": float(os.getenv("OVERLAP_THRESHOLD", 0.5)),
    "PROXIMITY_THRESHOLD": float(os.getenv("PROXIMITY_THRESHOLD", 10.0)),
    "FILTERING_SIZE_THRESHOLD": float(os.getenv("FILTERING_SIZE_THRESHOLD", 10.0)),
}

model = YOLO(config["PATH_TO_MODEL"])


def predict(image_file):
    """
    Predict the image using the custom YOLOv5 model from
    https://github.com/nedimcanulusoy/ui-component-detection.
    """
    image = Image.open(image_file)

    result = model.predict(source=image)

    return result[0].summary()


def filter_categories(result) -> list:
    """
    Define the confidence threshold and the list of categories to keep.
    Possible categories:
        "Image", "Text Button", "Text", "Input", "Icon", "List Item"
    """
    categories_to_keep = ["Image", "Text Button", "Input", "Icon", "List Item"]

    filtered_results = []
    for detection in result:
        if (
            detection["confidence"] >= config["CONFIDENCE_THRESHOLD"]
            and detection["name"] in categories_to_keep
        ):
            filtered_results.append(
                {
                    "box": {
                        "x1": detection["box"]["x1"],
                        "x2": detection["box"]["x2"],
                        "y1": detection["box"]["y1"],
                        "y2": detection["box"]["y2"],
                    },
                    "class": detection["class"],
                    "confidence": detection["confidence"],
                    "name": detection["name"],
                }
            )

    return filtered_results


def filter_small_boxes(filtered_results) -> list:
    """Remove boxes that are too small."""
    return [
        detection
        for detection in filtered_results
        if detection["box"]["x2"] - detection["box"]["x1"]
        > config["FILTERING_SIZE_THRESHOLD"]
        and detection["box"]["y2"] - detection["box"]["y1"]
        > config["FILTERING_SIZE_THRESHOLD"]
    ]


def filter_overlapping_boxes(filtered_results) -> list:
    """Remove overlapping boxes by keeping the one with the highest confidence."""

    def calculate_iou(box1, box2):
        box1_shapely = shapely_box(box1["x1"], box1["y1"], box1["x2"], box1["y2"])
        box2_shapely = shapely_box(box2["x1"], box2["y1"], box2["x2"], box2["y2"])
        intersection = box1_shapely.intersection(box2_shapely).area
        union = box1_shapely.union(box2_shapely).area
        return intersection / union

    non_overlapping_results = []
    for i, detection in enumerate(filtered_results):
        keep = True
        for j, other_detection in enumerate(filtered_results):
            if i != j:
                iou = calculate_iou(detection["box"], other_detection["box"])
                if iou > config["OVERLAP_THRESHOLD"]:
                    if detection["confidence"] < other_detection["confidence"]:
                        keep = False
                        break
        if keep:
            non_overlapping_results.append(detection)

    return non_overlapping_results


def filter_proximity(non_overlapping_results) -> list:
    """Remove boxes that are too close to each other."""

    def calculate_distance(box1, box2):
        return math.sqrt(
            (box1["x1"] - box2["x1"]) ** 2 + (box1["y1"] - box2["y1"]) ** 2
        )

    final_results = []

    for i, detection in enumerate(non_overlapping_results):
        keep = True
        for j, other_detection in enumerate(non_overlapping_results):
            if i != j:
                distance = calculate_distance(detection["box"], other_detection["box"])
                if (
                    distance < config["PROXIMITY_THRESHOLD"]
                ):  # Define a suitable threshold for proximity
                    keep = False
                    break
        if keep:
            final_results.append(detection)

    return final_results


def plot_results(image_file, final_results, output_file) -> dict:
    """Plot the final results on the image."""
    image = Image.open(image_file)
    _, ax = plt.subplots(1)
    ax.imshow(image)
    ax.axis("off")  # Turn off the axes
    image_width, image_height = image.size

    for detection in final_results:
        box = detection["box"]
        x_percentage = (box["x1"] / image_width) * 100
        y_percentage = (box["y1"] / image_height) * 100
        rect = patches.Rectangle(
            (box["x1"], box["y1"]),
            box["x2"] - box["x1"],
            box["y2"] - box["y1"],
            linewidth=2,
            edgecolor="r",
            facecolor="none",
        )
        ax.add_patch(rect)
        plt.text(
            box["x1"],
            box["y1"] - 10,
            f"({detection['name']}, {x_percentage:.0f}%, {y_percentage:.0f}%)",
            color="red",
            fontsize=3,
            weight="bold",
            path_effects=[
                path_effects.Stroke(linewidth=1, foreground="black"),
                path_effects.Normal(),
            ],
        )

    plt.tight_layout(pad=0)  # Adjust layout to minimize padding
    plt.savefig(output_file, dpi=500, bbox_inches="tight", pad_inches=0)

    return {i: detection for i, detection in enumerate(final_results)}


def format_output(final_results, width, height) -> dict:
    """Format the output for the LLM."""
    formatted_output = {}
    for i, detection in enumerate(final_results):
        box = detection["box"]
        center_x = int(((box["x1"] + box["x2"]) / 2) / width * 100)
        center_y = int(((box["y1"] + box["y2"]) / 2) / height * 100)
        formatted_output[f"button_{i}"] = {"x": center_x, "y": center_y}
    return formatted_output


def detect_ui_elements(image_file, output_file) -> dict:
    """Detect the UI elements in the image."""
    result = predict(image_file)

    filtered_results = filter_categories(result)

    filtered_results = filter_small_boxes(filtered_results)

    non_overlapping_results = filter_overlapping_boxes(filtered_results)

    final_results = filter_proximity(non_overlapping_results)

    plot_results(image_file, final_results, output_file)

    image = Image.open(image_file)
    width, height = image.size

    return format_output(final_results, width, height)
