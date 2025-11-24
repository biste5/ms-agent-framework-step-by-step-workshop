from agent_framework import AgentRunContext
from typing import Callable, Awaitable

async def logging_agent_middleware(
    context: AgentRunContext,
    next: Callable[[AgentRunContext], Awaitable[None]],
) -> None:
    """Simple middleware that logs agent execution."""
    print("FROM MIDDLEWARE (Agent): Starting GreetingAgent...")

    # Continue to agent execution
    await next(context)

    print("FROM MIDDLEWARE (Agent): GreetingAgent finished!")
