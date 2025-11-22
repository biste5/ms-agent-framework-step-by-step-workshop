import os
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    instructions="You are good at telling tales.",
    name="Joker"
)


async def run_basic(prompt: str) -> None:
    result = await agent.run(prompt)
    print(f"\nAgent: {result.text}\n")


async def run_streaming(prompt: str) -> None:
    print("\nAgent (streaming): ", end="", flush=True)
    async for update in agent.run_stream(prompt):
        if update.text:
            print(update.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Lab 01: First Agent ===")
    print("Type 'exit' at any prompt to quit. Choose between basic run and streaming modes.\n")

    while True:
        mode = input("Mode ([1] basic, [2] streaming): ").strip().lower()
        if mode in {"exit", "quit"}:
            print("Goodbye!")
            break
        if mode not in {"1", "2", "basic", "stream", "streaming"}:
            print("Please choose '1' for basic or '2' for streaming.\n")
            continue

        prompt = input("Enter your prompt: ").strip()
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not prompt:
            print("Prompt cannot be empty.\n")
            continue

        if mode in {"1", "basic"}:
            await run_basic(prompt)
        else:
            await run_streaming(prompt)


if __name__ == "__main__":
    asyncio.run(main())
