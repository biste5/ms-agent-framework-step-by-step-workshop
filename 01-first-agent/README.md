# Lab01 - Create and run your first agent

In this opening exercise you’ll learn how to build and run a basic conversational agent using the Microsoft Agent Framework. We’ll guide you through setting up your environment, installing dependencies, and writing a minimal agent that interacts with a Chat Completion LLM to generate responses. The tutorial uses Azure OpenAI as the inference backend, but any LLM compatible with the framework’s chat client protocol can be used in its place, including providers such as OpenAI, Google Gemini, Anthropic Claude, Mistral, Cohere, DeepSeek, Amazon Bedrock (which exposes models like Claude, Llama, and Mistral), and open-source models served locally through Ollama. Each provider comes with its own considerations—such as Bedrock requiring AWS credentials or Ollama needing to run locally—but all of them work seamlessly as long as they implement an `IChatClient`-compatible interface.

Step by step, you’ll define the agent’s behavior, run it locally, and interact with it through a simple command-line interface. This initial agent will form the foundation for more complex scenarios later in the workshop, giving you a practical starting point for exploring the full capabilities of the Agent Framework.

## 1. Create the folder for the lab and open VS Code

Let's create the folder and then open the workshop folder with VS Code for ease of use:

```
mkdir 01-first-agent
code .
```

Now, within the 01-first-agent create the file app.py.

## 2. Create the agent

- First, create a chat client for communicating with Azure OpenAI and use the same login as you used when authenticating with the Azure CLI in the [Prerequisites](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/run-agent?pivots=programming-language-python#prerequisites) step.
- Then, create the agent, providing instructions and a name for the agent.

```python
import os
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
```

## 3. Running the agent interactively

`app.py` now ships with a small CLI so you can try multiple prompts without editing the file. Option **1** performs a regular `agent.run(...)` call and prints the full response once it is ready.

```python
async def run_basic(prompt: str) -> None:
    result = await agent.run(prompt)
    print(f"\nAgent: {result.text}\n")

async def main() -> None:
    while True:
        mode = input("Mode ([1] basic, [2] streaming): ").strip().lower()
        ...
        if mode in {"1", "basic"}:
            await run_basic(prompt)
```

Run it with:

```bash
python 01-first-agent/app.py
```

Example session:

```
Mode ([1] basic, [2] streaming): 1
Enter your prompt: Tell me a joke about a pirate

Agent: Why did the pirate go on vacation? He needed some arrrrr and relaxation.
```

Type `exit` at either prompt to stop the loop.

## 4. Running the agent with streaming

Choose option **2** (or type `stream` / `streaming`) in the same CLI to observe token-by-token output. Behind the scenes the helper below calls `agent.run_stream(...)` and prints each update as it arrives.

```python
async def run_streaming(prompt: str) -> None:
    print("\nAgent (streaming): ", end="", flush=True)
    async for update in agent.run_stream(prompt):
        if update.text:
            print(update.text, end="", flush=True)
    print("\n")
```

```
Mode ([1] basic, [2] streaming): 2
Enter your prompt: Tell me a tale about a pirate

Agent (streaming): Once upon a tide... <tokens continue to stream>
```

This interactive approach lets you switch between blocking and streaming runs without changing any code.

## 5. Running the agent with a ChatMessage: The Power of Structured Multimodal Messages

Instead of a simple string, you can also provide one or more `ChatMessage` objects to the `run` and `run_stream` methods.

#### Understanding `ChatMessage`

`ChatMessage` is a structured object that represents a **single message within a conversation**, enabling clear definition of the message's properties:

1.  **`role` (Sender):** Specifies who sent the message (e.g., `Role.USER`, `Role.AGENT`/`MODEL`).
2.  **`contents` (Payload):** A list of content elements, supporting mixed data types.

#### Why Use `ChatMessage`?

The main advantage is support for **multimodality** and structured conversation context:

| Benefit                | Description                                                  |
| :--------------------- | :----------------------------------------------------------- |
| **Multimodal Support** | Allows you to combine various data types—text, images, video URIs—within a single, cohesive message. |
| **Clear Context**      | Explicitly setting the `role` is vital for managing conversation history and turns effectively. |

#### The Example Explained: A Multimodal Request

This code illustrates how `ChatMessage` allows the agent to process both a textual instruction and a visual element simultaneously.

```python
from agent_framework import ChatMessage, TextContent, UriContent, Role

DEFAULT_IMAGE = "https://www.fotosanimales.es/wp-content/uploads/2017/12/pinguino.jpg"
DEFAULT_PROMPT = "Tell me a joke about this image."


def build_message(image_url: str) -> ChatMessage:
    contents = [TextContent(text=DEFAULT_PROMPT)]
    contents.append(UriContent(uri=image_url, media_type="image/jpeg"))
    return ChatMessage(role=Role.USER, contents=contents)


async def main() -> None:
    print(f"Default image URL: {DEFAULT_IMAGE}\n")
    while True:
        image_url = input("Image URL [Enter for default]: ").strip()
        if image_url.lower() in {"exit", "quit"}:
            break
        if not image_url:
            image_url = DEFAULT_IMAGE
            print(f"Using default image: {DEFAULT_IMAGE}")

        message = build_message(image_url)
        result = await agent.run(message)
        print(f"\nAgent: {result.text}\n")


asyncio.run(main())
```

Run `python 01-first-agent/app-chat-message.py`, paste any image URL (or press Enter to reuse the default penguin photo that the script displays), and type `exit` when finished.

## 📝 Lab 01 Conclusion: Your First Agent

You have successfully completed the first foundational lab of the Microsoft Agent Framework workshop.

------

#### Key Takeaways from Lab 01

- **Agent Creation:** You learned how to instantiate a conversational agent by connecting it to an **Azure OpenAI** backend using the `AzureOpenAIChatClient` and defining its personality via the `instructions` parameter (e.g., "You are good at telling jokes.").
- **Basic Execution (`.run`):** You executed a simple, single-turn query using a standard Python string as input.
- **Streaming Execution (`.run_stream`):** You implemented response streaming, demonstrating how the framework processes and delivers tokens in real-time, which is essential for a responsive user experience.
- **Multimodal Communication (`ChatMessage`):** You explored the advanced pattern of using the `ChatMessage` object, which is crucial for sending **multimodal requests** (combining text and external media like images via URIs) and for managing complex **multi-turn conversations** effectively.

This initial agent serves as the basic building block for all subsequent, more complex scenarios in this workshop.

------

### Code Reference

The complete code implementations for this lab can be found in the repository:

- **[`app.py`](app.py):** Interactive CLI that lets you switch between basic `.run()` calls and streaming responses (Steps 2–4).
- **[`app-chat-message.py`](app-chat-message.py):** Interactive ChatMessage sample that accepts custom text plus an optional image URL (Step 5).

------

## 🔗 Navigation

- **[🏠 Back to Workshop Home](../README.md)** — Return to the main workshop page and prerequisites
- **[➡️ Next: Lab 02 — Multi-Turn Conversations](../02-multi-turn-conversations/README.md)** — Continue to the next lab on managing multi-turn conversations

------