#!/usr/bin/env python
# _*_coding: utf-8 _*_
# Coder: Whitejoce

from openai import OpenAI
from rich.console import Console
from rich.prompt import Prompt

# API Configuration
API_CONFIG = {
    "url": "",
    "api_key": "",
    "model": "qwen-plus-2025-04-28"
}

# Validate API configuration
assert API_CONFIG["url"] and API_CONFIG["api_key"], "Please fill in the correct url and api_key"

# Initialize Rich components and OpenAI client
console = Console()
client = OpenAI(api_key=API_CONFIG["api_key"], base_url=API_CONFIG["url"])

class Agent:
    def __init__(self, role, system_prompt):
        self.role = role
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
    
    def get_response(self):
        response, reasoning = get_chat_response(client, self.messages)
        self.add_message("assistant", response)
        return response, reasoning

def get_chat_response(client: OpenAI, messages: list[dict[str, str]]) -> tuple[str, str]:
    """Get chat response"""
    response = client.chat.completions.create(
        model=API_CONFIG["model"], messages=messages, stream=True
    )
    reply_chunk, reasoning_chunk = [], []
    full_reply = ""
    has_reasoning = False
    
    with console.status("[bold green]Thinking...[/bold green]") as status:
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                reply_chunk.append(content)
                full_reply += content
            
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                has_reasoning = True
                reasoning_content = chunk.choices[0].delta.reasoning_content
                reasoning_chunk.append(reasoning_content)
                status.stop()
                console.print(reasoning_content, end="")
                
    if has_reasoning:
        print()
        
    return "".join(reply_chunk), "".join(reasoning_chunk)

def dump_markdown(messages: list[dict[str, str]], file_name: str) -> None:
    """Convert message history to Markdown format"""
    md = ""
    for item in messages:
        if item["role"] == "system":  # Skip system messages
            continue
        role_label = "**Agent_A:**\n" if item["role"] == "assistant" else "**Agent_B:**\n"
        md += f"{role_label} {item['content']}\n"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(md)

def create_summary(keyword: str, agent_a: Agent, agent_b: Agent, file_name: str):
    """Create conversation summary"""
    summary_prompt = f"""
You just participated in a conversation about [{keyword}].

Based on the entire conversation, please summarize the following:

1. What were the core points you raised in this discussion?
2. What issues were of common interest? Where were there disagreements?
3. Were any new research directions or unsolved problems discovered?

Please organize your answer in bullet points, with concise language and clear logic.
""".strip()
    
    # Add summary prompt to both agents
    agent_a.add_message("user", summary_prompt)
    agent_b.add_message("user", summary_prompt)
    
    # Get summaries from both agents
    reply_a, _ = agent_a.get_response()
    reply_b, _ = agent_b.get_response()
    
    # Combine summaries
    combined_messages = agent_a.messages.copy()
    combined_messages.append({"role": "user", "content": f"{reply_b}"})
    
    dump_markdown(combined_messages, file_name)

def create_prompts(keyword):
    """Create conversation prompts"""
    prompt_a = f"""
You will now engage in an open dialogue with another AI about [{keyword}].

Please express your views freely based on your understanding of this topic, and try to:

1. Ask thought-provoking questions;
2. Challenge or follow up on the other's viewpoints;
3. Encourage exploration of new perspectives, rather than simply repeating known content.

Please participate in the conversation naturally, without presupposing positions, but maintaining critical thinking.
""".strip()

    prompt_b = f"""
You will engage in an open dialogue with another AI about [{keyword}].

Please actively participate in the discussion based on your knowledge of the topic:

1. Respond to questions or viewpoints raised by the other;
2. Try to raise new questions or perspectives;
3. Aim to push the conversation toward a deeper understanding.

Please participate with an equal and open attitude, neither blindly following nor stubbornly insisting on your own views.
""".strip()
        
    return prompt_a, prompt_b

if __name__ == "__main__":
    keyword = Prompt.ask("[bold blue]key word> [/bold blue]")
    prompt_a, prompt_b = create_prompts(keyword)
    
    # Initialize two agents
    agent_a = Agent("A", prompt_a)
    agent_b = Agent("B", prompt_b)
    
    conversation_log = []
    
    while True:
        try:
            # Save current session
            dump_markdown(agent_a.messages, "chat_history.md")
            
            user_input = Prompt.ask("[bold blue]Continue (q/quit to exit, s/save to save)? [/bold blue]")
            if user_input.lower() in ["q", "quit"]:
                break
            elif user_input.lower() in ["s", "save"]:
                create_summary(keyword, agent_a, agent_b, "summary.md")
                console.print("[green]Conversation saved successfully![/green]")
                break

            # Get Agent A's reply and add it to Agent B's messages
            response_a, _ = agent_a.get_response()
            agent_b.add_message("user", response_a)
            
            # Get Agent B's reply and add it to Agent A's messages
            response_b, _ = agent_b.get_response()
            agent_a.add_message("user", response_b)

        except Exception as error:
            console.print(f"[red]Error occurred:[/red] {str(error)}")
            continue
