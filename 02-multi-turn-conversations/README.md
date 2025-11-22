# Lab02 - Multi Turn Conversations

This lab shows you how to have a multi-turn conversation with an agent, where the agent is built on the Azure OpenAI Chat Completion service. Agent Framework supports many different types of agents. Here, we are going to use an agent based on a Chat Completion service, but all other agent types are run in the same way. For more information on other agent types and how to construct them, see the [Agent Framework user guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview).

## **Understanding How Conversation History Is Stored in Multi-Turn Agents**

When building multi-turn conversational agents, it’s important to understand where the conversation history lives, because the storage model changes depending on the type of service powering the `AIAgent`.

### **1. ChatCompletion-based Agents (local or SDK-driven)**

In this model, conversation history is fully managed by the client application. The `AgentThread` object stores every message exchanged with the user, and the entire history must be sent back to the model on each request. The agent has no backend persistence, so your application is responsible for maintaining context, managing message growth, and handling state across turns.

### **2. Azure AI Agent Service (within Azure AI Foundry)**

When using the Azure AI Agent Service, the conversation is persisted directly inside the Azure platform. Instead of sending all past messages with every call, the client only provides a conversation reference (such as a conversation ID). Azure handles retrieving the history, maintaining continuity, and storing new messages automatically. This reduces payload size, improves performance, and centralizes state management in a secure, scalable service.

In conclusion, the key distinction is simple: `ChatCompletion` agents store their own memory on the client, while Azure AI Agent Service stores and manages the memory for you. Understanding this difference helps you architect multi-turn agents that scale cleanly and take advantage of Azure’s built-in conversation management.

## Running the agent with a multi-turn conversation

Agents are stateless and do not maintain any state internally between calls. To have a multi-turn conversation with an agent, you need to create an object to hold the conversation state and pass this object to the agent when running it.

For this lab, you can keep the code required to create the agent as in [Lab01](..\01-first-agent\README.md). 
Then, to create the conversation state object, call the `get_new_thread()` method on the agent instance. The interactive sample in `app.py` performs this step for you every time it sees a brand-new conversation id.

> [!NOTE]
> **Simulating User Interaction:** The CLI in this lab mimics a chat interface. In your applications the prompts would typically come from:
> - User input in a chat UI (web, mobile, desktop)
> - Voice commands transcribed to text
> - Messaging platforms (Teams, Slack, etc.)
> - API requests from other services
>
> Each entry you type is treated as a new user turn, and the conversation id you choose determines which history the agent reuses.

`app.py` now exposes a small CLI that keeps a default thread alive for you. Each time you submit a message, the script routes it to the same underlying `AgentThread`, so the model remembers earlier context for that conversation.

```python
threads: dict[str, AgentThread] = {}

def get_thread(session_id: str):
    if session_id not in threads:
        threads[session_id] = agent.get_new_thread()
    return threads[session_id]

async def main() -> None:
    while True:
        session_id = input("Conversation id [default=general]: ").strip() or "general"
        ...
        thread = get_thread(session_id)
        result = await agent.run(prompt, thread=thread)
        print(f"[{session_id}] {result.text}")
```

Run it with:

```bash
python 02-multi-turn-conversations/app.py
```

Example session (single thread):

```
Conversation id [default=general]:
User message: Help me brainstorm an opening line for a customer presentation

[general] Let's set a collaborative tone: "Thanks for partnering with us on this journey—I'd love to align on your priorities before we dive into solutions."

Conversation id [default=general]:
User message: Can you rephrase it to sound more energetic and add emojis?

[general] "We're thrilled to team up with you—let's explore your top goals before we jump in! 🚀🤝"
```

This loop keeps the conversation state between turns automatically.

## Single agent with multiple conversations

It is possible to have multiple, independent conversations with the same agent instance by creating multiple `AgentThread` objects. These threads can then be used to maintain separate conversation states for each conversation. The conversations will be fully independent of each other, since the agent does not maintain any state internally. The CLI automatically provisions a new thread for each unique conversation id you enter.

Use different conversation ids (for example `project-alpha` and `project-beta`) to create parallel threads. The script prints “Created new conversation ...” the first time it sees a new id, so you always know when a fresh thread is being initialized. Type `list` to see all active sessions or `exit` any time to quit. Example:

```
Conversation id [default=general]: project-alpha
User message: Help me outline onboarding steps for a new hire program

[project-alpha] ...

Conversation id [default=general]: project-beta
User message: Draft a status update email for stakeholders

[project-beta] ...

Conversation id [default=general]: project-alpha
User message: Add friendly reminders and timelines

[project-alpha] ...
```

Each label (`pirate`, `robot`, etc.) maps to its own `AgentThread`, keeping conversation history isolated just as two different users would experience in production.

## 📝 Lab 02 Conclusion: Multi-Turn Conversations

You have successfully completed the second lab of the Microsoft Agent Framework workshop, learning how to manage stateful conversations with agents.

------

### Key Takeaways from Lab 02

- **Conversation State Management:** You learned that agents are stateless and require an `AgentThread` object to maintain conversation history across multiple turns.
- **Multi-Turn Conversations:** You implemented conversations where the agent can reference previous messages, enabling contextual responses using the `thread` parameter in `.run()` and `.run_stream()` methods.
- **Multiple Independent Conversations:** You explored how a single agent instance can handle multiple, independent conversations simultaneously by creating separate `AgentThread` objects for each conversation.
- **Storage Models:** You understood the key difference between ChatCompletion-based agents (client-side history management) and Azure AI Agent Service (server-side history persistence), which is crucial for architecting scalable multi-turn solutions.

This knowledge of conversation management prepares you for more advanced agent patterns involving tools and function calling in the next lab.

------

### Code Reference

The complete code implementation for this lab can be found in the repository:

- **[`app.py`](app.py):** Interactive CLI for routing prompts to one or more conversation threads.

------

## 🔗 Navigation

- **[⬅️ Back: Lab 01 — Create and Run Your First Agent](../01-first-agent/README.md)** — Return to the previous lab
- **[🏠 Back to Workshop Home](../README.md)** — Return to the main workshop page and prerequisites
- **[➡️ Next: Lab 03 — Function Tools](../03-function-tools/README.md)** — Continue to the next lab where you extend agents with custom function tools

------