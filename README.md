# llm2llm  
<p align="center">
  <a href="./README_CN.md">中文文档</a>
</p>

This is an AI conversation simulator project suitable for various scenarios such as academic discussions, idea exchanges, and knowledge exploration. It implements a system where two AI agents conduct dialogues using the OpenAI API, with support for streaming output, saving conversation logs in Markdown format, and generating summaries.

---

## ✅ **Function Overview**

A dual-AI-character (Agent_A and Agent_B) dialogue system with the following main features:

- Uses `rich` for beautiful terminal output;
- Supports fetching model responses via streaming API;
- Allows saving conversations into Markdown files;
- Can generate discussion summaries;
- Provides user control over the conversation flow: continue / save / exit.

---

## 🧠 **Advantages Analysis**

1. **Highly Extensible**:
   - You can easily switch models or add more agents by simply modifying configurations or adding new classes.
2. **Comprehensive Logging and Summarization**:
   - Both the conversation process and final summary can be saved to files, making it convenient for later review and analysis.

---

## 🧪 Example Usage

```python
# API Configuration
API_CONFIG = {
    "url": "",
    "api_key": "",
    "model": "qwen-plus-2025-04-28"
}
```

After filling in the `url` and `api_key`, run the script:

```bash
$ python llm2llm_en.py
key word> Quantum Computing
Continue (q/quit to exit, s/save to save)?
```

You can press Enter to let the two Agents continue the conversation automatically, type `s` to save and exit, or `q` to quit directly.
