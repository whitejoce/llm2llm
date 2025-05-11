#!/usr/bin/env python
# _*_coding: utf-8 _*_
# Coder: Whitejoce

from openai import OpenAI
from rich.console import Console
from rich.prompt import Prompt

# API 配置
API_CONFIG = {
    "url": "",
    "api_key": "",
    "model": "qwen-plus-2025-04-28"
}

# 验证API配置
assert API_CONFIG["url"] and API_CONFIG["api_key"], "请填写正确的url和api_key"

# 初始化Rich组件和OpenAI客户端
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
    """获取聊天响应"""
    response = client.chat.completions.create(
        model=API_CONFIG["model"], messages=messages, stream=True
    )
    reply_chunk, reasoning_chunk = [], []
    full_reply = ""
    has_reasoning = False
    
    with console.status("[bold green]思考中...[/bold green]") as status:
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
    """将消息记录转换为Markdown格式"""
    md = ""
    for item in messages:
        if item["role"] == "system":  # 跳过系统消息
            continue
        role_label = "**Agent_A:**\n" if item["role"] == "assistant" else "**Agent_B:**\n"
        md += f"{role_label} {item['content']}\n"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(md)

def create_summary(keyword: str, agent_a: Agent, agent_b: Agent, file_name: str):
    """创建对话摘要"""
    summary_prompt = f"""
你刚刚参与了一场关于【{keyword}】的对话。

请根据全部对话内容，总结以下内容：

1. 你在这场讨论中提出的核心观点是什么？
2. 有哪些问题是你们共同关注的？哪些存在分歧？
3. 是否发现了新的研究方向或尚未解决的问题？

请以条列形式组织回答，语言简洁、逻辑清晰。
""".strip()
    
    # 添加总结提示到两个代理
    agent_a.add_message("user", summary_prompt)
    agent_b.add_message("user", summary_prompt)
    
    # 获取两个代理的总结
    reply_a, _ = agent_a.get_response()
    reply_b, _ = agent_b.get_response()
    
    # 整合总结
    combined_messages = agent_a.messages.copy()
    combined_messages.append({"role": "user", "content": f"{reply_b}"})
    
    dump_markdown(combined_messages, file_name)

def create_prompts(keyword):
    """创建对话提示"""
    prompt_a = f"""
现在你将与另一个AI进行一场关于【{keyword}】的开放式对话。

请基于你对这个主题的理解，自由表达你的观点，并尝试：

1. 提出有深度的问题；
2. 对对方的观点进行追问或挑战；
3. 鼓励探索新的视角，而非简单重复已知内容。

请以自然的方式参与对话，不预设立场，但保持批判性思维。
""".strip()

    prompt_b = f"""
你将与另一个AI进行一场关于【{keyword}】的开放式对话。

请根据你对该主题的知识，积极参与讨论：

1. 回应对方提出的问题或观点；
2. 尝试提出新的问题或角度；
3. 力求推动对话走向更深层次的理解。

请以平等、开放的态度参与，不盲从也不固执己见。
""".strip()
        
    return prompt_a, prompt_b

if __name__ == "__main__":
    keyword = Prompt.ask("[bold blue]key word> [/bold blue]")
    prompt_a, prompt_b = create_prompts(keyword)
    
    # 初始化两个代理
    agent_a = Agent("A", prompt_a)
    agent_b = Agent("B", prompt_b)
    
    conversation_log = []
    
    while True:
        try:
            # 保存当前会话
            dump_markdown(agent_a.messages, "chat_history.md")
            
            user_input = Prompt.ask("[bold blue]Continue (q/quit to exit, s/save to save)? [/bold blue]")
            if user_input.lower() in ["q", "quit"]:
                break
            elif user_input.lower() in ["s", "save"]:
                create_summary(keyword, agent_a, agent_b, "summary.md")
                console.print("[green]已保存对话记录！[/green]")
                break

            # 获取代理A的回复并添加到代理B的消息中
            response_a, _ = agent_a.get_response()
            agent_b.add_message("user", response_a)
            
            # 获取代理B的回复并添加到代理A的消息中
            response_b, _ = agent_b.get_response()
            agent_a.add_message("user", response_b)

        except Exception as error:
            console.print(f"[red]发生错误:[/red] {str(error)}")
            continue
