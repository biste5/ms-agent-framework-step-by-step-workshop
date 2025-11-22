# Lab 04 — Human-in-the-loop approvals

In this lab you extend your agent with tools that have real-world impact. Some operations, like sending money, must be reviewed by a human before the agent is allowed to execute them. The Agent Framework surfaces these approval requirements, lets you gather the user’s decision, and then resume the agent flow with the additional input.

You will build an interactive console application that:

- registers multiple banking tools (balance inquiries and payments)
- keeps a running conversation with `ChatAgent`
- detects every approval request the model issues
- gathers one approval response per function call
- sends all approvals back in a single follow-up run tied to the previous output

> [!TIP]
> Approval requests often arrive in groups (for example, the model may try to call more than one tool in the same turn). The code you will write handles any number of requests safely.

------

## Why `ChatAgent` instead of the earlier helpers?

Labs 01–03 relied on **single-run convenience helpers**: you instantiated a lightweight agent, issued a single request, and immediately discarded the state. That approach is perfect for demos, but it breaks down when you need:

- **Persistent memory** so every turn shares the same conversation context and tool plan.
- **Centralized tool governance** (registration, approval policies, and diagnostics) for an entire session.
- **Lifecycle hooks** that keep long-running threads, streaming callbacks, or background work alive between turns.
- **Human approvals** that can pause a run, wait on input, and then resume exactly where the model left off.

`ChatAgent` is the framework’s stateful orchestration surface. It keeps the thread, tool catalog, and model configuration alive until you decide to shut it down. That is why this lab—and any other workflow that mixes tools, memory, and human approvals—should be built on `ChatAgent` rather than the one-shot helper APIs from earlier labs.

------

## 1. Function tools with approval requirements

Create a file named [`bank_functions.py`](bank_functions.py) that contains the tools your agent can call. Use the `@ai_function` decorator to specify metadata. Setting `approval_mode="always_require"` marks a tool as high risk: the agent must stop and ask the user before executing it.

```python
from typing import Annotated
from agent_framework import ai_function

@ai_function(approval_mode="always_require")
def submit_payment(
    amount: Annotated[float, "Payment amount in USD"],
    recipient: Annotated[str, "Recipient name or vendor ID"],
    reference: Annotated[str, "Payment memo or invoice reference"],
) -> str:
    return (
        f"Payment of ${amount:.2f} to '{recipient}' has been submitted "
        f"with reference '{reference}'."
    )

@ai_function()
def get_account_balance(
    account_id: Annotated[str, "Internal account identifier"],
) -> str:
    return f"Account {account_id} currently holds $9,876.54."
```

- `submit_payment` is approval-gated because it moves money.
- `get_account_balance` is informational only and can run immediately.

------

## 2. Instantiating a stateful `ChatAgent`

With the tools defined, wire them into `ChatAgent`. This lab uses `AzureOpenAIChatClient` with `AzureCliCredential` so the same authentication flow you configured in earlier labs is reused.

```python
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
```

Key points:

- The agent holds onto a conversation thread (`agent.get_new_thread()`), so every turn references the same context.
- Passing both tools lets the model decide whether it needs balances or payments (and request approval when required).

------

## 3. Running the interactive console loop

`app.py` starts by creating a thread, greeting the user, and then blocking for console input. Each line the user types is sent through `agent.run(...)`:

```python
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("exit", "quit"):
        break
    if not user_input:
        continue

    result = await agent.run(user_input, thread=thread)
```

- Typing `exit` or `quit` ends the loop.
- Blank lines are ignored to keep the conversation clean.
- Every run references the same thread so the agent keeps its memory and tool plan.

------

## 4. Handling one or many approval requests

When the model decides to call an approval-gated tool, the run returns one `FunctionApprovalRequestContent` per call in `result.user_input_requests`. The sample inspects every request, presents the function call to the human, and collects a yes/no decision.

```python
if result.user_input_requests:
    approval_messages: list[ChatMessage] = []
    for req in result.user_input_requests:
        print(f"- Function: {req.function_call.name}")
        print(f"  Arguments: {req.function_call.arguments}")
        approved = input("Approve ... (yes/no): ").strip().lower() == "yes"
        approval_messages.append(
            ChatMessage(role=Role.USER, contents=[req.create_response(approved)])
        )
```

- `req.create_response(True)` embeds the approval decision inside a message the agent framework understands.
- The code builds one `ChatMessage` per request so all approvals stay tied to the right function call.

------

### What exactly is `ChatMessage`?

`ChatMessage` is the strongly typed envelope the Agent Framework uses to move information between the human, the agent, and the model. Each message contains:

- a `role` (`Role.USER`, `Role.ASSISTANT`, or `Role.TOOL`) so the model knows who is “speaking”; and
- a `contents` list with structured parts—plain text, images, or special objects such as the approval payload returned by `req.create_response(...)`.

Because approvals must be explicitly tied to the original tool call, we instantiate a new `ChatMessage` for every decision and drop the `req.create_response(...)` result into its `contents`. When we pass that array of messages back to `agent.run(...)`, the framework can replay the human’s decisions verbatim into the model conversation and safely continue execution.

------

## 5. Resuming the agent with `prior_run`

Once every approval decision is captured, the app sends them back to the agent in a single follow-up call. Passing `prior_run=result` informs the framework that these approvals correspond to the earlier tool proposals.

```python
followup = await agent.run(approval_messages, thread=thread, prior_run=result)
print("\nAgent:", followup.text)
```

- If the user approves the operation, the agent executes the tool and responds with the confirmation string returned by the function.
- If the user rejects any call, the agent is told about the denial and can explain that the payment was cancelled.

------

## 6. Putting it all together

Run the lab with:

```bash
python 04-human-in-loop/app.py
```

Sample interaction:

```
You: please pay $1250 to Fabrikam for invoice 8831

=== APPROVALS REQUIRED ===
- Function: submit_payment
  Arguments: {"amount": 1250.0, "recipient": "Fabrikam", "reference": "invoice 8831"}
Approve 'submit_payment'? (yes/no): yes

Agent: Payment of $1250.00 to 'Fabrikam' has been submitted with reference 'invoice 8831'.
```

------

## 📝 Lab 04 Conclusion: Human-in-the-loop Approvals

You now have an agent that can safely execute high-impact tools only after a human explicitly approves each call. This mirrors real banking review flows while still letting the model plan, reason, and call multiple tools per turn.

------

#### Key Takeaways from Lab 04

- **`ChatAgent` unlocks full sessions:** Unlike the single-run helpers from previous labs, `ChatAgent` keeps memory, tool catalog, and lifecycle hooks alive for the entire console session—essential for human approvals.
- **Approval-aware tools are first-class:** Decorating tools with `approval_mode="always_require"` lets the framework pause execution automatically whenever the model proposes risky actions.
- **`ChatMessage` carries structured intent:** Wrapping each approval decision inside a `ChatMessage` keeps the association between a user’s decision and the exact function call the model proposed.
- **`prior_run` resumes safely:** By referencing the earlier run when sending approvals, the agent continues exactly where it paused, producing fluent follow-up responses.

This pattern is the foundation for any scenario where humans must stay in the loop—payments, policy updates, infrastructure changes, or other sensitive business operations.

------

### Code Reference

- [`app.py`](app.py) — interactive console agent that aggregates approvals before resuming the run.
- [`bank_functions.py`](bank_functions.py) — tool definitions for `submit_payment` (approval required) and `get_account_balance` (informational).

------

## 🔗 Navigation

- **[⬅️ Back: Lab 03 — Function Tools](../03-function-tools/README.MD)** — Review tool creation and class-based patterns.
- **[🏠 Back to Workshop Home](../README.md)** — Return to prerequisites and lab index.
- **[➡️ Next: Lab 05 — Advanced Agent Patterns](../05-advanced-agent-patterns/README.md)** — Continue into multi-step orchestration and escalation flows.

------

