import json
import os
from datetime import datetime

import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

SESSION_DIR = "sessions_file"
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def get_api_key():
    """优先读取 Streamlit secrets，其次读取环境变量。"""
    try:
        key = st.secrets.get("DEEPSEEK_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("DEEPSEEK_API_KEY", "")


def save_session():
    if st.session_state.current_session:
        new_session = {
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages,
            "nickname": st.session_state.nickname,
            "personality": st.session_state.personality,
        }
        os.makedirs(SESSION_DIR, exist_ok=True)
        with open(
            os.path.join(SESSION_DIR, f"{st.session_state.current_session}.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(new_session, f, ensure_ascii=False, indent=4)


def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def load_session_list():
    session_list = []
    if os.path.exists(SESSION_DIR):
        for filename in os.listdir(SESSION_DIR):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    return session_list


def load_session(session_name):
    try:
        path = os.path.join(SESSION_DIR, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            st.session_state.messages = session_data["messages"]
            st.session_state.nickname = session_data["nickname"]
            st.session_state.personality = session_data["personality"]
            st.session_state.current_session = session_name
    except Exception:
        st.error("会话加载失败，请检查会话名称是否正确！")


def delete_session(session_name):
    try:
        path = os.path.join(SESSION_DIR, f"{session_name}.json")
        if os.path.exists(path):
            os.remove(path)
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("会话删除失败，请检查会话名称是否正确！")


system_prompt = """
                你叫 %s,现在是用户的真实伴侣,请完全带入伴侣角色,
                规则:
                    1:每次只回复一条消息
                    2.禁止任何场景或状态描述性文字
                    3.匹配用户语言
                    4.回复简短,像微信聊天一样
                    5.有需要的话可以用emoji表情
                    6.用符合伴侣性格方式对话
                    7.回复内容,要求体现伴侣性格特征
                伴侣性格:
                    - %s
                你必须严格遵守上述规则来回复用户
"""

st.title("AI智能伴侣")
st.logo(os.path.join("resources", "logo.png"))

if "messages" not in st.session_state:
    st.session_state.messages = []
if "nickname" not in st.session_state:
    st.session_state.nickname = "小甜甜"
if "personality" not in st.session_state:
    st.session_state.personality = "活泼开朗的东北姑娘"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

api_key = get_api_key()
if not api_key:
    st.error(
        "未检测到 DeepSeek API Key。请设置环境变量 `DEEPSEEK_API_KEY`，"
        "或在 `.streamlit/secrets.toml` 中配置。"
    )
    st.stop()

client = OpenAI(api_key=api_key, base_url=BASE_URL)

with st.sidebar:
    st.subheader("AI控制面板")
    if st.button("新建会话", width="stretch", icon="💘"):
        save_session()
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()

    st.markdown("会话历史")
    session_list = load_session_list()
    if not session_list:
        st.caption("暂无历史会话")
    else:
        for session in session_list:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    session,
                    width="stretch",
                    icon="🗂️",
                    key=f"load_{session}",
                    type="primary"
                    if session == st.session_state.current_session
                    else "secondary",
                ):
                    load_session(session)
                    st.rerun()
            with col2:
                if st.button(
                    "", width="stretch", icon="❌", key=f"delete_{session}"
                ):
                    delete_session(session)
                    st.rerun()

    st.divider()
    st.subheader("伴侣信息")

    nickname = st.text_input(
        "昵称", placeholder="请输入昵称", value=st.session_state.nickname
    )
    if nickname:
        st.session_state.nickname = nickname

    personality = st.text_area(
        "性格", placeholder="请输入性格", value=st.session_state.personality
    )
    if personality:
        st.session_state.personality = personality

prompt = st.chat_input("请输入您要问的问题:")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    messages = [
        {
            "role": "system",
            "content": system_prompt
            % (st.session_state.nickname, st.session_state.personality),
        },
        *st.session_state.messages,
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True,
        )

        response_message = st.empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                response_message.chat_message("assistant").write(full_response)
    except Exception as e:
        st.error(f"调用大模型失败：{e}")
        st.stop()

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
    save_session()