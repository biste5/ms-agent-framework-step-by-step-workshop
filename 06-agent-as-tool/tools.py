from typing import Annotated
from pydantic import Field


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Return a simple weather report for the requested location."""
    return f"The weather in {location} is cloudy with a high of 15°C."
