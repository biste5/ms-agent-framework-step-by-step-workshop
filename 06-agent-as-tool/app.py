import os
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from tools import get_weather

weather_agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]).create_agent(
        name="WeatherAgent",
        description="An agent that answers questions about the weather.",
        instructions="You answer questions about the weather.",
        tools=get_weather)


main_agent = AzureOpenAIChatClient(credential=AzureCliCredential()).create_agent(
    instructions="You are a helpful assistant who responds in French.",
    tools=weather_agent.as_tool()
)