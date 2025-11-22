import os
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from weather_tools import WeatherTools

tools = WeatherTools()

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    instructions="You are a concise weather assistant. Call the right tool and respond with the tool output only.",
    tools=[tools.get_weather, tools.get_max_temperature]
)


async def main() -> None:
    print("=== Lab 03: Function Tools (class-based) ===")
    print("Ask about current weather or maximum temperatures. Type 'exit' to quit.\n")

    while True:
        question = input("Weather assistant question: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            print("Question cannot be empty.\n")
            continue

        result = await agent.run(question)
        print(f"\nAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())