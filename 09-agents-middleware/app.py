import asyncio
import os
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from middleware import logging_agent_middleware
from functions_middleware import get_time, logging_function_middleware

# Load environment variables from .env file
load_dotenv()


async def main():
   
    credential = AzureCliCredential()

    async with AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ["AOAI_ENDPOINT"],
        deployment_name=os.environ["AOAI_DEPLOYMENT"],
        api_key=os.environ.get("AOAI_API_KEY")
    ).as_agent(
        name="GreetingAgent",
        instructions=(
            "You are a friendly greeting assistant."
        ),
        tools=[get_time],
        middleware=[
            logging_agent_middleware,
            logging_function_middleware,
        ],
    ) as agent:
        result = await agent.run("Hi there! What time is it right now?")
        print(result.text)
    

if __name__ == "__main__":
    asyncio.run(main())


    