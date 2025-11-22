# Using an agent as a function tool
This lab shows you how to use an agent as a function tool, so that one agent can call another agent as a tool.

## Create and use an agent as a function tool
You can use a `ChatAgent` as a function tool by calling `.as_tool()` on the agent and providing it as a tool to another agent. This allows you to compose agents and build more advanced workflows.

First, create a function tool that will be used by your agent that's exposed as a function. Place it in [`tools.py`](tools.py) so it can be imported by other modules in this lab.

```python
from typing import Annotated
from pydantic import Field


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C."
```


