import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint="https://warstandalone.openai.azure.com/",
    deployment_name="dep-gpt-5-mini"
).create_agent(
    instructions="You are good at telling tales.",
    name="Joker"
)

async def main():
    async for update in agent.run_stream("Tell me a tale about a pirate."):
        if update.text:
            print(update.text, end="", flush=True)
    print()  # New line after streaming is complete

asyncio.run(main())
