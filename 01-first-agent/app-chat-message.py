import os
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import ChatMessage, TextContent, UriContent, Role
from azure.identity import AzureCliCredential

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    instructions="You are good at telling jokes.",
    name="Joker"
)


message = ChatMessage(
    role=Role.USER,
    contents=[
        TextContent(text="Tell me a joke about this image?"),
        UriContent(uri="https://www.fotosanimales.es/wp-content/uploads/2017/12/pinguino.jpg", media_type="image/jpeg")
    ]
)

async def main():
    result = await agent.run(message)
    print(result.text)

asyncio.run(main())
