import os
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from tools import get_weather

# Weather-focused agent identical to the default sample
weather_agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    name="WeatherAgent",
    description="An agent that answers questions about the weather.",
    instructions="You answer questions about the weather.",
    tools=get_weather,
)

# Convert agent to tool with custom metadata so the orchestrator exposes richer docs
weather_tool = weather_agent.as_tool(
    name="WeatherLookup",
    description="Look up weather information for any location",
    arg_name="query",
    arg_description="The weather query or location",
)

main_agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    instructions="You are a helpful assistant who responds in French.",
    tools=weather_tool,
)


async def compare_agents(location: str) -> None:
    """Show the difference between direct and tool-mediated weather answers."""

    question = f"What is the weather like in {location}?"

    direct_response = await weather_agent.run(question)
    print("\n[WeatherAgent direct]")
    print(direct_response.text)

    tool_response = await main_agent.run(question)
    print("\n[MainAgent using WeatherLookup tool]")
    print(tool_response.text)


async def main() -> None:
    print("=== Agent as Tool (custom metadata) ===")
    print("Compare direct WeatherAgent answers with the WeatherLookup tool (type 'exit' to stop).\n")

    while True:
        location = input("City or country: ").strip()
        if not location:
            continue
        if location.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        await compare_agents(location)


if __name__ == "__main__":
    asyncio.run(main())
