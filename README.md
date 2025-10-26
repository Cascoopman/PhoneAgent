# Phone Agent

An autonomous AI agent that controls your iPhone using Google's ADK (Agent Development Kit) and Gemini's spatial understanding capabilities. The agent can see, understand, and interact with your phone's interface through screen mirroring and computer vision.

## Demo

https://github.com/user-attachments/assets/3e535db6-96ec-4ce8-83ca-b2af999fbe11


## Features

- **Autonomous Phone Control**: AI-powered agent that can navigate and interact with iOS interfaces
- **Visual Understanding**: Uses Gemini's spatial understanding to locate and identify UI elements
- **Natural Language Control**: Give high-level instructions and let the agent figure out the steps
- **Smart Navigation**: Automatic screenshot analysis, pointer movement, clicking, scrolling, and text entry
- **Loop Control**: Built-in pause and human intervention capabilities for safety

## How It Works

1. **Screen Mirroring**: Uses macOS's screen capture to monitor a mirrored iPhone display (via QuickTime or similar)
2. **Visual Analysis**: Gemini Pro analyzes screenshots to locate UI elements using spatial understanding
3. **Action Execution**: PyAutoGUI controls the mouse/keyboard to interact with the mirrored display
4. **Agent Loop**: Google ADK orchestrates the autonomous decision-making and tool usage

## Prerequisites

Grant cursor the accessibility to:
- 'Allow the application to control your computer'
- 'Screen & System Audio Recording'

**Platform Support**: Built for MacOS, other platforms might not be supported.

**Requirements**:
- macOS (for `screencapture` command)
- Python 3.12+
- Google Cloud Project with Vertex AI enabled
- iPhone with screen mirroring capability
- uv ([download here](https://docs.astral.sh/uv/getting-started/installation/))

## Installation

1. **Clone the repository**
```sh
git clone https://github.com/Cascoopman/PhoneAgent.git
cd PhoneAgent
```

2. **Set up environment**
```sh
# Copy environment template
cp phone_agent/.env.local phone_agent/.env
```

3. **Configure your environment variables** in `phone_agent/.env`:
   - `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
   - `GOOGLE_CLOUD_LOCATION`: GCP region (default: us-central1)
   - `GEMINI_PRO_MODEL`: Model to use (e.g., gemini-2.5-pro-preview-03-25)
   - `PHONE_PASSWORD`: Your phone's password (optional, for automated unlock)
   - Screen bounds and crop settings (adjust based on your display setup)

4. **Install dependencies**
```sh
uv sync
```

## Configuration

### Screen Mirroring Setup

1. Connect your iPhone to your Mac through Screen Mirroring
2. Position the mirrored display on your screen
3. Calibrate the screen size and cropping settings (see below)

### Display Calibration

Update these values in your `.env` file based on your screen setup:

- `MIRRORING_X_BOUND` / `MIRRORING_Y_BOUND`: The width/height of your mirrored phone display
- `IMAGE_CROP_BOX`: Screen region to capture (left, top, right, bottom)
- `HOME_BUTTON_X` / `HOME_BUTTON_Y`: Position of the home button/gesture area
- `SCREEN_Y_INVERSION`: Screen height for coordinate transformation

## Usage

```python
from phone_agent.agent import root_agent

# Start the agent with a task
root_agent.run("Open Safari and search for weather")
```

The agent will:
1. Take a screenshot of the current state
2. Analyze the UI using Gemini's spatial understanding
3. Determine the next action needed
4. Execute pointer movements, clicks, scrolls, or text entry
5. Verify the result and continue until the task is complete

## Project Structure

```
phone_agent/
├── agent.py           # Main agent configuration
├── tools/
│   ├── navigation.py  # Mouse/keyboard control (click, scroll, type)
│   ├── vision.py      # Screenshot capture and UI element detection
│   └── loop.py        # Agent loop control (pause, human intervention)
└── prompts/
    ├── agent.j2       # Main agent instructions
    └── vision.j2      # Vision model instructions
```

## Known Issues

### todo
pip install google-adk[eval] does not work
it should be pip install 'google-adk[eval]'. update the docs!

## Safety Features

- **Human Intervention**: Agent can request human assistance when uncertain
- **Pause Loop**: Ability to pause the autonomous loop
- **Explanation Required**: All tool calls require explanation of intent
- **Password Protection**: Prompts before entering sensitive information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.
