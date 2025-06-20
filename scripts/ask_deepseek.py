#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
组合检索 + DeepSeek 生成回答
需要环境变量：
  DEESEEK_API_KEY   DeepSeek 账户的 API Key
"""

import os, textwrap, json
from pathlib import Path

from openai import OpenAI
from scripts.retrieve_chunks import search 
from dotenv import load_dotenv
import json
import re


load_dotenv() 



DEESEEK_BASE_URL = "https://api.deepseek.com"
MODEL_NAME       = "deepseek-chat"
TEMPERATURE      = 0.3
TOP_K_CONTEXT    = 5 

client = OpenAI(
    api_key=os.getenv("DEESEEK_API_KEY"),
    base_url=DEESEEK_BASE_URL
)

def parse_json_from_llm(raw_text: str):
    # 去除 ```json 或 ``` 包裹
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)

def rewrite_query_with_deepseek(question: str) -> str:
    prompt = f"""请将以下问题改写为更适合检索文档的表达方式，使其更清晰、具体，并尽可能贴近文档中可能出现的表述风格：
请注意，你输出的结果我会直接用于embed 模型的检索，所以请确保改写后的问题能够更好地匹配文档内容，不需要更多的解释。    
原始问题：{question}
重写后："""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context_text = "\n\n".join(
        f"【出处：{c['source_file']}#{c['chunk_index']}】\n{c['text']}"
        for c in context_chunks
    )
    return textwrap.dedent(f"""\
        请结合以下资料回答问题，并以 JSON 格式返回：

        {{
        "answer": "...",
        "citations": [
            {{
            "source": "xxx.txt#3",
            "quote": "被引用的原文内容"
            }},
            ...
        ]
        }}

        资料如下：
        {context_text}

        问题：{question}
        """)


def ask(question: str):
    rewritten = rewrite_query_with_deepseek(question)
    print(f"\n📝 重写后的检索问题：{rewritten}\n")
    chunks = search(rewritten, TOP_K_CONTEXT)
    prompt = build_prompt(question, chunks)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE
    )
    raw_content = response.choices[0].message.content.strip()

    try:
        parsed = parse_json_from_llm(raw_content)

        answer = parsed["answer"]
        citations = parsed.get("citations", []) 
    except json.JSONDecodeError:
        print("❌ 无法解析为 JSON，返回原始内容")
        answer = raw_content
        citations = []
    
    return answer, chunks, citations


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ask with RAG + DeepSeek")
    parser.add_argument("question", nargs="+", help="要提问的问题")
    args = parser.parse_args()

    q = " ".join(args.question)
    answer, used_chunks = ask(q)

    print("\n=== 🎯 答案 ===\n")
    print(answer)

    print("\n=== 📑 引用的文档段落 (top-k) ===")
    for c in used_chunks:
        print(f"- {c['source_file']}#{c['chunk_index']} (dist={c['distance']:.4f})")
