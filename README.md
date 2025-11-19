# Microsoft Agent Framework Step by Step Workshop

Hands-on, step-by-step guide to building and operating AI agents with Microsoft’s Agent Framework.

This repository provides the end-to-end materials for a hands-on workshop focused on building, operating, and scaling AI Agents with Microsoft’s Agent Framework. It brings together architecture guidance, multi-agent design patterns, workflow orchestration examples, Responsible AI practices, and secure deployment strategies tailored for enterprise scenarios.

Inside this repo you’ll find structured labs, reference implementations, and modular components that demonstrate how to connect agents with MCP servers, integrate external systems through typed workflows, implement human-in-the-loop flows, and run agents safely within private network environments. Everything is designed to help teams move from conceptual understanding to real-world application—covering low-code agents, data-driven agents, and advanced multi-agent coordination.

This workshop reflects the collective learnings from partner engagements across the Americas, offering a practical path for architects and developers to adopt agentic patterns, accelerate solution delivery, and build AI-first applications with confidence.

## Prerequisites

Before you begin, ensure you have the following prerequisites:

- [Python 3.10 or later](https://www.python.org/downloads/)
- [Azure OpenAI service endpoint and deployment configured](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/create-resource)
- [Azure CLI installed](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) and [authenticated (for Azure credential authentication)](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)
  - For [these](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively?view=azure-cli-latest#sign-in-with-a-browser) exercises this is the recommended authentication method for your CLI
- [User has the `Cognitive Services OpenAI User` or `Cognitive Services OpenAI Contributor` roles for the Azure OpenAI resource.](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/role-based-access-control)

> [!NOTE]
>
> You can also use VS Code to follow the labs in this workshop. Please make sure you are signed in to VS Code using the **same Azure AD user account that has access to the Azure OpenAI resource**, so that the Azure extension can authenticate correctly and allow the CLI and SDK to run against your Azure environment.

> [!IMPORTANT]
>
> Clear any existing Azure OpenAI environment variables before using Azure AD authentication. 
> If you have previously set `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, or `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` environment variables, they will take precedence over the credentials passed in code and may cause authentication failures with old/invalid values.

## Prepare Environment

To keep the setup lightweight and avoid downloading the `agent-framework` package inside every lab folder, this workshop uses a **single shared virtual environment** created at the **root of the repository**. All lab folders (`01-first-agent`, `02-agents`, etc.) will reuse the same environment.

This approach keeps installations consistent, reduces disk usage, and ensures that any updates to dependencies automatically apply across all exercises.

### Create the virtual environment at the root of the repo

Before proceeding with any lab, create a `.venv` folder in the root directory:

> [!NOTE]
>
> #### **About executables:**
>
>  Depending on your operating system, Python may be invoked as `py`, `python`, or `python3`.
>  Replace the command accordingly:
>
> - Windows → `py` or `python`
> - macOS / Linux → `python3`
>
> Examples below use `py`, but you may substitute it with the one that works in your environment.

------

### 1. Create and activate the environment

```
py -m venv .venv
```

Activate it:

#### **macOS / Linux:**

```
source .venv/bin/activate
```

#### **Windows:**

```
.venv\Scripts\activate
```

------

### 2. Upgrade pip (recommended)

```
py -m pip install --upgrade pip
```

------

### 3. Install the Agent Framework package

```
pip install agent-framework
```

------

## Lab01 - Create and run your first agent

In this opening exercise you’ll learn how to build and run a basic conversational agent using the Microsoft Agent Framework. We’ll guide you through setting up your environment, installing dependencies, and writing a minimal agent that interacts with a Chat Completion LLM to generate responses. The tutorial uses Azure OpenAI as the inference backend, but any LLM compatible with the framework’s chat client protocol can be used in its place, including providers such as OpenAI, Google Gemini, Anthropic Claude, Mistral, Cohere, DeepSeek, Amazon Bedrock (which exposes models like Claude, Llama, and Mistral), and open-source models served locally through Ollama. Each provider comes with its own considerations—such as Bedrock requiring AWS credentials or Ollama needing to run locally—but all of them work seamlessly as long as they implement an `IChatClient`-compatible interface.

Step by step, you’ll define the agent’s behavior, run it locally, and interact with it through a simple command-line interface. This initial agent will form the foundation for more complex scenarios later in the workshop, giving you a practical starting point for exploring the full capabilities of the Agent Framework.

### 1. Create the folder for the lab and open VS Code

Let's create the folder and then open the workshop folder with VS Code for ease of use:

```
mkdir 01-first-agent
code .
```

Now, within the 01-first-agent create the file app.py.

### 2. Create the agent

- First, create a chat client for communicating with Azure OpenAI and use the same login as you used when authenticating with the Azure CLI in the [Prerequisites](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/run-agent?pivots=programming-language-python#prerequisites) step.
- Then, create the agent, providing instructions and a name for the agent.

Python

```python
import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint="[YOUR_ENDPOINT_NAME]",
    deployment_name="[YOUR_DEPLOYMENT_NAME]"
).create_agent(
    instructions="You are good at telling jokes.",
    name="Joker"
)
```

### 3. Running the agent

To run the agent, call the `run` method on the agent instance, providing the user input. The agent will return a response object, and accessing the `.text` property provides the text result from the agent.

Python

```python
async def main():
    result = await agent.run("Tell me a joke about a pirate.")
    print(result.text)

asyncio.run(main())
```

### 4. Running the agent with streaming

Observe how easy is to run the agent with streaming with the agent framework: call the `run_stream` method on the agent instance, providing the user input. The agent will stream a list of update objects, and accessing the `.text` property on each update object provides the part of the text result contained in that update. 

For you to notice the streaming, change the `instructions` to: `"You are good at telling tales."` and the prompt to `"Tell me a tale about a pirate"`

Python

```python
async def main():
    async for update in agent.run_stream("Tell me a tale about a pirate."):
        if update.text:
            print(update.text, end="", flush=True)
    print()  # New line after streaming is complete

asyncio.run(main())
```

You will see the streaming in action!

