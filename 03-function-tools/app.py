import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from function_tools import get_weather

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint="https://warstandalone.openai.azure.com/",
    deployment_name="dep-gpt-5-mini"
).create_agent(
    instructions="You are a helpful assistant",
    tools=[get_weather]  
)


async def main():
    result = await agent.run("What is the weather like in Amsterdam?")
    print(result.text)

asyncio.run(main())