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