# Lab10 - Persisting and Resuming Agent Conversations
This tutorial shows how to persist an agent conversation (AgentThread) to storage and reload it later.

When hosting an agent in a service or even in a client application, you often want to maintain conversation state across multiple requests or sessions. By persisting the AgentThread, you can save the conversation context and reload it later.