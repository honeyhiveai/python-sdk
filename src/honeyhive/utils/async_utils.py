import asyncio
from typing import Any, Coroutine

def run_async_coro(
    tasks: list[Coroutine] | Coroutine,
    times: int | None = None
) -> Any | Coroutine:
    
    # run the tasks in parallel
    async def gather_async(*tasks):
        return await asyncio.gather(*tasks)
    
    async def single_task(task):
        if asyncio.iscoroutine(task):
            return await task
        else:
            return task
    
    async def run_multiple_times(coro, times):
        return await asyncio.gather(*[
            coro
            for _ in range(times)
        ])
    
    if not isinstance(tasks, (list, tuple)):
        coroutine = single_task(tasks)
    else:
        coroutine = gather_async(*tasks)
    
    if times is not None:
        coroutine = run_multiple_times(coroutine, times)
    
    # if we are in a running event loop, return coroutine to be awaited
    if asyncio.get_event_loop().is_running():
        return coroutine
    
    return asyncio.run(coroutine)

def run_async(coro):
    """
    Run a coroutine in a synchronous context by creating a new event loop.

    This function is safe to use when no other asyncio loop is running.
    
    Args:
        coro: A coroutine object to run.

    Returns:
        The result of the coroutine.
    """
    # Create a new event loop.
    loop = asyncio.new_event_loop()
    try:
        # Set the new event loop as the current loop.
        asyncio.set_event_loop(loop)
        # Run the coroutine until it completes and return its result.
        return loop.run_until_complete(coro)
    finally:
        # Close the loop to free up resources.
        loop.close()
        # Reset the current event loop to prevent any potential memory issues.
        asyncio.set_event_loop(None)