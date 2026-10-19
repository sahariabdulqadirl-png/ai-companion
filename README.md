# AI 智能伴侣

一个基于 **Streamlit + DeepSeek** 的 AI 聊天伴侣应用。你可以自定义伴侣的昵称和性格，与 TA 像微信聊天一样对话，并将会话保存在本地。

## 功能特性

- 自定义伴侣昵称与性格，AI 会按设定的人设回复
- 流式输出，逐字显示回复内容
- 多会话管理：新建、切换、删除历史会话
- 会话自动保存为本地 JSON 文件
- 简洁的 Streamlit 网页界面

## 项目结构

```
ai-companion/
├── app.py                 # 应用入口
├── requirements.txt       # 依赖列表
├── resources/
│   └── logo.png           # 侧边栏 Logo
├── .streamlit/
│   └── secrets.toml.example
├── .env.example
└── .gitignore
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/sahariabdulqadirl-png/ai-companion.git
cd ai-companion
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

本项目需要 DeepSeek API Key，请在 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请。

**方式一：环境变量（推荐）**

PowerShell：

```powershell
$env:DEEPSEEK_API_KEY = "sk-你的密钥"
```

macOS / Linux：

```bash
export DEEPSEEK_API_KEY="sk-你的密钥"
```

**方式二：Streamlit secrets**

复制示例文件并填入密钥：

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

```toml
DEEPSEEK_API_KEY = "sk-你的密钥"
```

### 4. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

## 可选配置

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 无（必填） |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名称 | `deepseek-chat` |

## 安全说明

- 请勿将 API Key 提交到仓库。项目已通过 `.gitignore` 忽略 `.env` 和 `.streamlit/secrets.toml`。
- 会话记录保存在 `sessions_file/`，该目录同样不会被提交。

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。