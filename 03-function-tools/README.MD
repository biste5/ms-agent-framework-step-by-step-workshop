# Lab03 - Using function tools with an agent

This lab shows you how to use function tools with an agent, where the agent is built on the Azure OpenAI Chat Completion service.

### **Understanding Which Agent Types Support Function Tools**

When working with the Agent Framework, it’s important to understand that **not all agent types are designed to accept custom function tools**. Some agents are implemented as **internal, task-specific components** with fixed capabilities; these agents operate inside workflows or graphs and are not extensible by the caller. They execute their built-in logic but do not allow you to attach your own functions, APIs, or MCP tools.

Examples of these **non-extensible internal agents** include:

- **Retrieval-focused agents** that implement a predefined RAG pipeline.
   These agents expose retrieval behavior only and do not accept user-defined function tools.
- **Routing or decision agents** that evaluate inputs and choose a path.
   Their behavior is fixed to decision logic and cannot be extended with custom functions.
- **Workflow executor agents** used internally by graph nodes.
   These agents run orchestration logic and are not meant to host external tools.
- **System agents used by server-side reasoning**, verification, or runtime operations.
   These are internal components that are not exposed for customization.

In contrast, **developer-defined agents**—such as **ChatClientAgent**, **ReAct-based agents**, **Plan-Execute agents**, and the agents you build inside **Azure AI Foundry using the Agent Framework**—are fully extensible. These agents support user-provided function tools, custom APIs, MCP servers, and any external logic your application requires. They are the correct choice whenever you need to integrate business systems, call external services, or compose multi-tool agents.

This distinction helps clarify why the example uses `ChatClientAgent`: it is one of the agent types specifically designed to support function tools, making it suitable for building richer, tool-augmented multi-turn conversational experiences.

## Create the agent with function tools

Function tools are just custom code that you want the agent to be able to call when needed. You can turn any Python function into a function tool by passing it to the agent's `tools` parameter when creating the agent.

If you need to provide the agent with clearer and more detailed information about a function or its parameters—so it can accurately decide which tool to call—you can combine Python’s `Annotated` type hints with Pydantic’s `Field`. Pydantic is a data-modeling library that turns your Python type annotations into structured, validated schemas, allowing each parameter to include natural-language descriptions, examples, and constraints. When the Agent Framework reads these schemas, the agent gains a much deeper understanding of what each parameter represents, which improves tool selection and helps it generate fully valid arguments during multi-function reasoning.

Here is an example of a simple function tool that fakes getting the weather for a given location. It uses type annotations to provide additional descriptions about the function and its location parameter to the agent. You can create this function in a new file called `function_tools.py`.

```python
from typing import Annotated
from pydantic import Field

def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C."
```

You can also use the `ai_function` decorator to explicitly specify the function's name and description:

```python
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function

@ai_function(name="weather_tool", description="Retrieves weather information for any location")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    return f"The weather in {location} is cloudy with a high of 15°C."
```

If you don't specify the `name` and `description` parameters in the `ai_function` decorator, the framework will automatically use the function's name and docstring as fallbacks.

When creating the agent, you can now provide the function tool to the agent, by passing it to the `tools` parameter. Don't forget to import the function at the top of your `app.py` file, so the agent can use it.

```python
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from function_tools import get_weather

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint="[YOUR_ENDPOINT]",
    deployment_name="[YOUR_DEPLOYMENT_NAME]"
).create_agent(
    instructions="You are a helpful assistant",
    tools=[get_weather]  
)

```

Now you can just run the agent as normal, and the agent will be able to call the `get_weather` function tool when needed.

Python

```python
async def main():
    result = await agent.run("What is the weather like in Amsterdam?")
    print(result.text)

asyncio.run(main())
```

You can find the complete code for this lab in the [`app.py`](app.py) and [`function_tools.py`](function_tools.py) files.



## Create a class with multiple function tools

You can also create a class that contains multiple function tools as methods. This can be useful for organizing related functions together or when you want to pass state between them. Let's create it in a new file called `weather_tools.py`:

Python

```python
from typing import Annotated
from pydantic import Field


class WeatherTools:
    def get_weather(
        self,
        location: Annotated[str, Field(description="The location to get the weather for.")],
    ) -> str:
        """Get the weather for a given location."""
        return f"The weather in {location} is cloudy with a high of 15°C."

    def get_max_temperature(
        self,
        location: Annotated[str, Field(description="The location to get the maximum temperature for.")],
    ) -> str:
        """Get the maximum temperature expected for the day in a given location."""
        return f"The maximum temperature expected in {location} today is 22°C."
```

When creating the agent, you can now provide all the methods of the class as functions:

```python
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from weather_tools import WeatherTools

tools = WeatherTools()

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint="[YOUR_ENDPOINT]",
    deployment_name="[YOUR_DEPLOYMENT_NAME]"
).create_agent(
    instructions="You are a helpful weather assistant. You don't give additional help.",
    tools=[tools.get_weather, tools.get_max_temperature]  
)


async def main():
    # Test both tools
    result1 = await agent.run("What is the instant weather in Amsterdam?")
    print("Basic weather query:")
    print(result1.text)
    print("\n" + "="*50 + "\n")
    
    result2 = await agent.run("What is the maximum temperature expected today in Tokyo?")
    print("Maximum temperature query:")
    print(result2.text)

asyncio.run(main())
```
You can also decorate the functions with the same `ai_function` decorator as before.

Find the complete code for this example in the [`app2.py`](app2.py) and [`weather_tools.py`](weather_tools.py) files.

## 📝 Lab 03 Conclusion: Function Tools with Agents

You have successfully completed the third lab of the Microsoft Agent Framework workshop, learning how to extend agents with custom function tools.

------

#### Key Takeaways from Lab 03

- **Function Tools Basics:** You learned how to turn any Python function into a function tool by passing it to the agent's `tools` parameter, enabling agents to execute custom code when needed.
- **Type Annotations and Pydantic:** You explored how to use Python's `Annotated` type hints with Pydantic's `Field` to provide clear descriptions and metadata about function parameters, helping the agent make better decisions about which tool to call.
- **AI Function Decorator:** You discovered the `@ai_function` decorator for explicitly specifying function names and descriptions, providing even more control over how the agent understands your tools.
- **Class-Based Tool Organization:** You implemented a class with multiple function tools as methods, demonstrating how to organize related functions and share state between them.
- **Agent Type Compatibility:** You understood the important distinction between extensible agents (like ChatClientAgent) that support custom function tools, and internal task-specific agents that have fixed capabilities.

This knowledge of function tools prepares you for building more sophisticated agents that can interact with external systems, APIs, and business logic in the next labs.

------

### Code Reference

The complete code implementations for this lab can be found in the repository:

- **[`app.py`](app.py)** and **[`function_tools.py`](function_tools.py):** Basic single-function tool example
- **[`app2.py`](app2.py)** and **[`weather_tools.py`](weather_tools.py):** Class-based multiple function tools example

------

## 🔗 Navigation

- **[⬅️ Back: Lab 02 — Multi-Turn Conversations](../02-multi-turn-conversations/README.md)** — Return to the previous lab
- **[🏠 Back to Workshop Home](../README.md)** — Return to the main workshop page and prerequisites
- **[➡️ Next: Lab 04 — Human-in-the-loop Approvals](../04-human-in-loop/README.md)** — Learn how to require human approvals before high-impact tool calls

------

