## 🚀 DocSearcher

一个基于 Streamlit 和 AI 向量搜索的文档问答系统。

---

## 📦 环境搭建步骤

### 1. 克隆项目

```bash
git clone https://github.com/mzyy1001/DocSearcher.git
cd DocSearcher
```

### 2. 创建虚拟环境（推荐 Python 3.10 或 3.9）

```bash
python3 -m venv venv
```

### 3. 激活虚拟环境

- **macOS / Linux：**

```bash
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ 运行方式

### 使用 Streamlit 启动前端：

```bash
streamlit run app.py
```

启动后浏览器会自动打开页面。如果没有，请手动访问终端显示的链接（通常是 [http://localhost:8501](http://localhost:8501)）。

---

## 📁 项目结构

```
.
├── app.py                # Streamlit 主应用入口
├── requirements.txt      # 项目依赖
├── scripts/              # 处理模型与文本的脚本
├── models/               # 本地保存的 embedding 模型（如 m3e）
├── vector_store/         # FAISS 索引与元数据存储
├── chunks/               # 拆分好的文档段落
├── .env                  # API 密钥等私密配置
```

---

## 🧠 注意事项

- 本项目使用 `sentence-transformers` 和 `faiss`，如需 GPU 加速可自行配置 CUDA。
- 如运行时遇到缺失模块或安装问题，建议确认 Python 版本兼容性（推荐 3.9 或 3.10），或执行：

```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

---

## 📮 联系方式

如有问题，欢迎提交 issue 或联系作者 `hongruichen2003@gmail.com`
