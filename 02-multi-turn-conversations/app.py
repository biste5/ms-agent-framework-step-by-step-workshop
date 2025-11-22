import os
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AOAI_ENDPOINT"],
    deployment_name=os.environ["AOAI_DEPLOYMENT"]
).create_agent(
    instructions="You are a helpful conversation coach who keeps context between turns.",
    name="Conversationalist"
)

threads: dict[str, object] = {}


def get_thread(session_id: str):
    if session_id not in threads:
        threads[session_id] = agent.get_new_thread()
        print(f"Created new conversation '{session_id}'.")
    return threads[session_id]


def list_sessions() -> None:
    if not threads:
        print("No active conversations yet. Start typing to create one.\n")
        return
    print("Active conversations:")
    for name in threads:
        print(f"- {name}")
    print()


async def main() -> None:
    print("=== Lab 02: Multi-Turn Conversations ===")
    print("Type a conversation name to route messages to that thread.")
    print("Commands: 'list' to show sessions, 'exit' to quit.\n")

    while True:
        session_id = input("Conversation id [default=general]: ").strip()
        if not session_id:
            session_id = "general"

        if session_id.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if session_id.lower() == "list":
            list_sessions()
            continue

        prompt = input("User message: ").strip()
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not prompt:
            print("Message cannot be empty.\n")
            continue

        thread = get_thread(session_id)
        result = await agent.run(prompt, thread=thread)
        print(f"\n[{session_id}] {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())