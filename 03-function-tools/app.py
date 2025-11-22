import os
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from function_tools import get_weather

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    instructions="You are a helpful assistant who calls tools when needed.",
    tools=[get_weather]
)


async def main() -> None:
    print("=== Lab 03: Function Tools (single function) ===")
    print("Ask about the weather in any location. Type 'exit' to quit.\n")

    while True:
        question = input("Weather question: ").strip()
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