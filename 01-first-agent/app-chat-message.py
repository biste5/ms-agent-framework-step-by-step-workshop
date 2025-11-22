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

DEFAULT_IMAGE = "https://www.fotosanimales.es/wp-content/uploads/2017/12/pinguino.jpg"
DEFAULT_PROMPT = "Tell me a joke about this image."


def build_message(image_url: str) -> ChatMessage:
    contents = [TextContent(text=DEFAULT_PROMPT)]
    if image_url:
        contents.append(UriContent(uri=image_url, media_type="image/jpeg"))
    return ChatMessage(role=Role.USER, contents=contents)


async def main() -> None:
    print("=== Lab 01: ChatMessage Demo ===")
    print("Provide an image URL (press Enter to use the default penguin photo). Type 'exit' to quit.\n")

    print(f"Default image URL: {DEFAULT_IMAGE}\n")

    while True:
        image_url = input("Image URL [Enter for default]: ").strip()
        if image_url.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not image_url:
            image_url = DEFAULT_IMAGE
            print(f"Using default image: {DEFAULT_IMAGE}")

        message = build_message(image_url)
        result = await agent.run(message)
        print(f"\nAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
