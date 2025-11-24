# Lab09 -  Adding Middleware to Agents

Learn how to add middleware to your agents in a few simple steps. Middleware allows you to intercept and modify agent interactions for logging, security, and other cross-cutting concerns.

## What is middleware in Agent Framework?
In Microsoft Agent Framework, middleware refers to pluggable components that wrap the agent execution pipeline without changing the agent’s domain logic. Each middleware implements the `AgentMiddleware` contract and can inspect or mutate inputs (`before_agent`, `before_tool`) and outputs (`after_agent`, `after_tool`) as requests flow through the stack. Because middlewares run in a chain, you can compose cross-cutting behaviors—telemetry, safety filters, caching, policy enforcement—once and apply them to every agent consistently, keeping the core reasoning focused on business goals while shared concerns stay centralized.

## Step 1: Create a Simple Agent

First, create a basic agent:

```python
import asyncio
import os
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient

async def main():
    credential = AzureCliCredential()

    async with AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ["AOAI_ENDPOINT"],
        deployment_name=os.environ["AOAI_DEPLOYMENT"],
    ).create_agent(
        name="GreetingAgent",
        instructions=(
            "Always greet the user and include the precise current time by calling the get_time tool "
            "before responding. If the tool fails, say you cannot determine the time."
        ),
    ) as agent:
        result = await agent.run("Hi there! What time is it right now?")
        print(result.text)

if __name__ == "__main__":
    asyncio.run(main())
```

Compared to earlier labs where the `ChatAgent` was instantiated directly, this pattern highlights the **Agent Framework client-first flow**:

- `credential = AzureCliCredential()` centralizes Microsoft Entra authentication. The object caches tokens under the hood, so every agent run reuses the same access token until it expires, avoiding repeated CLI prompts.
- `AzureOpenAIChatClient(...).create_agent()` returns an asynchronous context manager. Entering the `async with` block spins up the agent (registering it with Azure OpenAI if needed) and exiting the block guarantees cleanup and resource release—even when an exception happens.
- Lifecycle responsibilities (auth, retries, teardown) stay inside the client, so when you layer middleware later on, each request flows through a predictable pipeline. Your business logic only needs to send prompts, while cross-cutting behavior sits in middleware classes.

## Step 2: Create your middleware

With a working agent in place, define the middleware function that will wrap its execution. Middleware in Agent Framework receives the current `AgentRunContext` and a `next` callback. Call `await next(context)` to continue the pipeline; do your pre-/post-work on either side of that call.

Create `middleware.py` with the following content:

```python
from agent_framework import AgentRunContext
from typing import Awaitable, Callable

async def logging_agent_middleware(
    context: AgentRunContext,
    next: Callable[[AgentRunContext], Awaitable[None]],
) -> None:
    """Simple middleware that logs agent execution."""
    print("FROM MIDDLEWARE (Agent): Starting GreetingAgent...")

    await next(context)  # Invoke the next middleware or the agent itself

    print("FROM MIDDLEWARE (Agent): GreetingAgent finished!")
```

Why this structure matters:

- `context` exposes the inbound prompt, prior runs, and shared metadata so you can inspect or even mutate the call before the agent runs.
- `next` represents the rest of the middleware chain; omitting it would short-circuit execution, which is handy for guardrails but in this example we simply log before and after.
- Keeping middleware in its own module allows reuse across multiple agents—later steps will show how to register the same function for every pipeline stage you need.

## Step 3: Register the middleware when creating the agent

Finally, wire the middleware into the agent pipeline by importing it inside `app.py` and passing it to `create_agent`. Update the file so the top of the script includes the new import and the context manager receives the `middleware` argument:

```python
import asyncio
import os
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from middleware import logging_agent_middleware

async def main():
    credential = AzureCliCredential()

    async with AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ["AOAI_ENDPOINT"],
        deployment_name=os.environ["AOAI_DEPLOYMENT"],
    ).create_agent(
        name="GreetingAgent",
        instructions=(
            "Always greet the user and include the precise current time by calling the get_time tool "
            "before responding. If the tool fails, say you cannot determine the time."
        ),
        middleware=logging_agent_middleware,
    ) as agent:
        result = await agent.run("Hi there! What time is it right now?")
        print(result.text)
```

Key points:

- Importing from `middleware` keeps your agent file focused on orchestration while the reusable middleware logic lives elsewhere.
- Passing `middleware=logging_agent_middleware` attaches the function to the agent’s execution pipeline, so every run now emits the “FROM MIDDLEWARE” logs before and after the agent executes.
- You can pass additional middleware (e.g., a list) later; the argument accepts any callable that matches the `AgentRunContext` signature shown in Step 2.

## Step 4: Add function middleware for tool calls

Agent-level middleware catches every message before and after the agent runs, but you can also wrap **individual function tools**. This is useful when you want to log or guard specific tool invocations without touching the agent prompt flow.

Create `functions_middleware.py` with the following content:

```python
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
```

What’s happening here:

- `FunctionInvocationContext` exposes metadata about the tool being invoked (its name, arguments, return value). You can inspect or mutate the context before the function runs.
- `function_middleware` tags the coroutine so the framework routes it through the function middleware pipeline automatically.
- `next(context)` executes the actual tool (and any remaining tool middleware). Without this call the tool would never run, so handle short-circuiting carefully when building guardrails.
- By co-locating helper utilities (like `get_time()`) in the same module, you can register them as tools while reusing the same logging middleware, keeping observability consistent across all function invocations.

## Step 5: Attach the function middleware to your agent

Update `app.py` so the agent loads the new tool and middleware. Import the helpers and pass them to `create_agent`:

```python
import asyncio
import os
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from middleware import logging_agent_middleware
from functions_middleware import get_time, logging_function_middleware

async def main():
    credential = AzureCliCredential()

    async with AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ["AOAI_ENDPOINT"],
        deployment_name=os.environ["AOAI_DEPLOYMENT"],
    ).create_agent(
        name="GreetingAgent",
        instructions=(
            "Always greet the user and include the precise current time by calling the get_time tool "
            "before responding. If the tool fails, say you cannot determine the time."
        ),
        tools=[get_time],
        middleware=[
            logging_agent_middleware,
            logging_function_middleware,
        ],
    ) as agent:
        result = await agent.run("Hi there! What time is it right now?")
        print(result.text)
```

How this guarantees the function middleware fires:

- The system instructions explicitly tell the agent to call `get_time` before answering, and the user prompt asks for the current time, nudging the model to reach for the tool.
- Adding `tools=[get_time]` lets the agent call the `get_time` tool whenever the model decides it needs the current time.
- Passing both middleware functions in a list registers them in order. The agent middleware logs at the top level, then the function middleware logs every time the tool is invoked.
- When you run the script you will now see console output similar to:

    ```text
    FROM MIDDLEWARE (Agent): Starting GreetingAgent...
    FROM MIDDLEWARE (Function): Calling get_time
    FROM MIDDLEWARE (Function): Result => 14:03:12
    FROM MIDDLEWARE (Agent): GreetingAgent finished!
    <agent response here>
    ```

  Those extra lines confirm the function middleware is in the pipeline before the agent prints its final response.

------

## 📝 Lab 09 Conclusion: Middleware Everywhere

You layered both agent-level and function-level middleware onto an Azure OpenAI agent, forcing it to call a tool and proving each pipeline fires through log output. With middleware isolated in reusable modules, you can now bolt on logging, safety, caching, or policy enforcement without touching the agent instructions again.

------

#### Key Takeaways from Lab 09

- Agent middleware runs before and after every agent turn, making it perfect for logging or guardrails that must always execute.
- Function middleware wraps individual tools, so you can audit or short-circuit sensitive operations without rewriting prompts.

------

## 🔗 Navigation

- **[⬅️ Back: Lab 08 — Observability](../08-observability/README.md)** — Review how to emit OpenTelemetry traces for every agent run.
- **[🏠 Back to Workshop Home](../README.md)** — Return to the main index for setup steps and additional labs.
- **[➡️ Next: Lab 10 — Persisting Conversations](../10-persisting-conversations/README.md)** — Continue by storing agent state between turns.