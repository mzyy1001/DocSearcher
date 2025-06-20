#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动 Streamlit，然后用 pywebview 打开桌面窗口
"""

import subprocess, sys, threading, time, webbrowser
import requests, webview, os, signal

PORT = 8501                 # Streamlit 默认端口
URL  = f"http://localhost:{PORT}"

def ensure_requirements(require_file="requirements.txt"):
    if not os.path.exists(require_file):
        return
    missing = []
    with open(require_file, encoding="utf-8") as f:
        for line in f:
            pkg = line.strip().split("==")[0]
            if pkg and not importlib.util.find_spec(pkg.replace("-", "_")):
                missing.append(pkg)
    if missing:
        print(f"📦 正在安装缺失依赖：{', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing]
        )

def run_streamlit():
    # 启动 Streamlit，设置 headless / 禁用自动浏览器
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--browser.serverAddress", "127.0.0.1",
        "--server.port", str(PORT),
    ]
    # stderr/stdout 可重定向到 PIPE；这里直接继承终端
    return subprocess.Popen(cmd)

def wait_until_alive(url, timeout=30):
    for _ in range(timeout * 10):
        try:
            requests.get(url)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

def main():
    
    ensure_requirements()
    # 1️⃣ 启动后台 Streamlit
    p = run_streamlit()

    try:
        # 2️⃣ 等待服务就绪
        if not wait_until_alive(URL):
            print("❌ Streamlit 启动超时")
            p.terminate()
            sys.exit(1)

        # 3️⃣ 打开桌面窗口（800x600 可自行调整）
        webview.create_window(
            title="DocSearcher · DeepSeek QA",
            url=URL,
            width=1000,
            height=800,
            resizable=True,
            zoomable=True,
        )
        webview.start()
    finally:
        # 4️⃣ 关闭 Streamlit 进程
        if p.poll() is None:      # Still running
            if os.name == "nt":
                p.send_signal(signal.CTRL_BREAK_EVENT)
            p.terminate()

if __name__ == "__main__":
    main()
