import asyncio

from google.adk.tools import ToolContext


async def pause_loop(explanation: str, duration: int) -> dict:
    """
    Pauses your current task for a specified duration before resuming.
    Use this to wait for a specific event to occur before resuming your task
    without user intervention.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
        duration (int): The duration to pause the task in seconds.

    Returns:
        dict: The outcome of the pause.
    """
    await asyncio.sleep(duration)
    return {"status": "task continued after pause"}


def human_intervention(explanation: str, tool_context: ToolContext):
    """
    Interrupts the autonomous loop to allow for USER input and intervention.
    Call this *immediately* if you need USER input, have encountered an error twice,
    or when your task is complete.

    Args:
        explanation (str): One sentence explanation as to why this tool is being used, and how it contributes to the goal.
    """
    tool_context.actions.escalate = True
    return {}
