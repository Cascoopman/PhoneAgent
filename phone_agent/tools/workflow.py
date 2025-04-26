import asyncio

async def pause_workflow(explanation: str, duration: int) -> dict:
    """
    Pause your workflow for a specified duration before resuming.
    """
    await asyncio.sleep(duration)
    return {"status": "workflow continued after pause"}

