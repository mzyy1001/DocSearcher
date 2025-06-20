#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Streamlit front-end for Doc Searcher + DeepSeek QA
"""

import os, subprocess, sys, shutil, importlib.util, json, time
from pathlib import Path
import streamlit as st
import importlib.util



if importlib.util.find_spec("openai") is None:
    st.error("❌ 依赖未安装。请先在终端运行：\n\n`pip install -r requirements.txt`\n")
    st.stop()




# ----Config----
DATA_DIR = Path("data")
SCRIPTS_DIR = Path("scripts")   # 用于动态 import
REQUIRE_FILE = Path("requirements.txt")
CHUNK_SCRIPT = SCRIPTS_DIR / "chunk_text.py"
EMBED_SCRIPT = SCRIPTS_DIR / "embed_chunks.py"
M3E_MODEL_DIR = Path("models/m3e-base")
DOWNLOAD_SCRIPT = SCRIPTS_DIR / "download_m3e.py"

if not M3E_MODEL_DIR.exists():
    st.info("📥 检测到 m3e 模型未下载，正在自动下载 …")
    subprocess.check_call([sys.executable, DOWNLOAD_SCRIPT])
    st.success("✅ 模型下载完成")

# ----② Token 输入----
if "token" not in st.session_state:
    st.session_state["token"] = ""

if "token_confirmed" not in st.session_state:
    st.session_state["token_confirmed"] = False

st.title("📚 DocSearcher + DeepSeek QA Demo")

if not st.session_state["token_confirmed"]:
    st.subheader("🔐 输入 DeepSeek API Token")

    st.session_state["token"] = st.text_input("Token", type="password")

    if st.button("✅ 提交 Token"):
        if st.session_state["token"]:
            st.session_state["token_confirmed"] = True
            st.rerun()  # 🔄 刷新以进入主界面
        else:
            st.warning("请先输入 Token 再提交")
    st.stop()

os.environ["DEESEEK_API_KEY"] = st.session_state["token"]

# ----③ 文件上传----
st.header("上传资料文件")
uploaded = st.file_uploader(
    "支持 txt / docx / doc … 仅保留当前上传文件",
    type=["txt", "docx", "doc"],
)

def clean_and_save(file):
    # 清空 data 目录
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(exist_ok=True)

    save_path = DATA_DIR / file.name
    with open(save_path, "wb") as f:
        f.write(file.getbuffer())
    return save_path

def run_preprocess(filepath: Path):
    # 调用已有脚本：chunk → embed
    # 这里用 subprocess 简单调用；也可直接 import 调用函数
    subprocess.check_call([sys.executable, CHUNK_SCRIPT, str(filepath)])
    subprocess.check_call([sys.executable, EMBED_SCRIPT])

if "embedded" not in st.session_state:
    st.session_state["embedded"] = False

if uploaded and not st.session_state["embedded"]:
    saved_path = clean_and_save(uploaded)
    st.success(f"✅ 已保存到 {saved_path}")

    with st.spinner("⏳ 正在分块 / 嵌入 …"):
        run_preprocess(saved_path)

    st.success("📑 资料准备完毕！")
    st.session_state["ready"] = True
    st.session_state["embedded"] = True

if "answer" not in st.session_state:
    st.session_state["answer"] = ""
if "citations" not in st.session_state:
    st.session_state["citations"] = []
if "chunks" not in st.session_state:
    st.session_state["chunks"] = []

# ----④ 提问界面----
if st.session_state.get("ready"):
    from scripts.ask_deepseek import ask  # 动态 import，避免前面依赖未安装

    st.header("向资料提问")
    question = st.text_input("请输入问题")
    if st.button("🔍 提问") and question:
        with st.spinner("DeepSeek 生成中…"):
            answer, chunks ,citations = ask(question)
            st.session_state["answer"] = answer
            st.session_state["citations"] = citations

        if st.session_state["answer"]:
            st.subheader("🎯 答案")
            st.write(st.session_state["answer"])
            for c in st.session_state["citations"]:
                st.markdown(f"\"{c['quote']}\"\n\n")
