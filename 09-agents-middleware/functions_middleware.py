from agent_framework import FunctionInvocationContext, tool, function_middleware
from typing import Awaitable, Callable


@tool(name="get_time", description="Return the current time in HH:MM:SS format.")
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime

    return datetime.now().strftime("%H:%M:%S")


@function_middleware
async def logging_function_middleware(
    context: FunctionInvocationContext,
    call_next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Function middleware that logs function execution."""
    # Pre-processing: Log before function execution
    print(f"[Function] Calling {context.function.name}")

    # Continue to next middleware or function execution
    await call_next(context)

    # Post-processing: Log after function execution
    print(f"[Function] {context.function.name} completed")
