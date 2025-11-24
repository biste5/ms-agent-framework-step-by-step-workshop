from agent_framework import FunctionInvocationContext, ai_function, function_middleware
from typing import Awaitable, Callable


@ai_function(name="get_time", description="Return the current time in HH:MM:SS format.")
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime

    return datetime.now().strftime("%H:%M:%S")


@function_middleware
async def logging_function_middleware(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Middleware that logs function calls."""
    print(f"FROM MIDDLEWARE (Function): Calling {context.function.name}")

    await next(context)

    print(f"FROM MIDDLEWARE (Function): Result => {context.result}")
