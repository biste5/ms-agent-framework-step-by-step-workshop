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