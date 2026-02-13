from agent_framework import AgentContext
from typing import Callable, Awaitable

async def logging_agent_middleware(
    context: AgentContext,
    next: Callable[[], Awaitable[None]],
) -> None:
    """Simple middleware that logs agent execution."""
    print("FROM MIDDLEWARE (Agent): Starting GreetingAgent...")

    # Continue to agent execution
    await next()

    print("FROM MIDDLEWARE (Agent): GreetingAgent finished!")
