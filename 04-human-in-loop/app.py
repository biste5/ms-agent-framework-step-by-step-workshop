import asyncio
from agent_framework import ChatAgent, ChatMessage, Role
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from bank_functions import submit_payment, get_account_balance

# Stateful agent wired to Azure OpenAI plus both banking tools
agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(
        credential=AzureCliCredential(),
        endpoint="https://warstandalone.openai.azure.com/",
        deployment_name="dep-gpt-5-mini"
    ),
    name="FinanceAgent",
    instructions=(
        "You are an agent from Contoso Bank. You assist users with financial operations "
        "and provide clear explanations. For transfers only amount, recipient name, and reference are needed."
    ),
    tools=[submit_payment, get_account_balance],
)

async def main():
    # Preserve conversation memory across the entire console session
    thread = agent.get_new_thread()
    print("=== FinanceAgent - Interactive Session ===")
    print("Type 'exit' or 'quit' to end the conversation\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        print("\nAgent: ", end="", flush=True)
        result = await agent.run(user_input, thread=thread)

        if result.user_input_requests:
            print("\n\n=== APPROVALS REQUIRED ===")
            approval_messages: list[ChatMessage] = []
            # Surface every pending tool call and gather a decision per call
            for req in result.user_input_requests:
                print(f"- Function: {req.function_call.name}")
                print(f"  Arguments: {req.function_call.arguments}")
                approved = input(f"Approve '{req.function_call.name}'? (yes/no): ").strip().lower() == "yes"
                # Encode the approval/denial into a ChatMessage the framework consumes
                approval_messages.append(
                    ChatMessage(role=Role.USER, contents=[req.create_response(approved)])
                )

            # Resume the prior run once all approvals are ready
            followup = await agent.run(approval_messages, thread=thread, prior_run=result)
            print("\nAgent:", followup.text)
        else:
            print(result.text)

        print()

if __name__ == "__main__":
    asyncio.run(main())