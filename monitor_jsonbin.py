import streamlit as st
import os

from roles import get_role_prompt, get_break_rules
from logic import should_exit_by_user, should_exit_by_ai
from chat import chat_once
from jsonbin import get_latest_reply

def get_portrait():
    return """
 ______     ____     _           __                             
/_  __/__ _/ / /__  (_)__   ____/ /  ___ ___ ____               
 / / / _ `/ /  '_/ / (_-<  / __/ _ \/ -_) _ `/ _ \              
/_/  \_,_/_/_/\_\ /_/___/  \__/_//_/\__/\_,_/ .__/              
  _   ___ __                            ___/_/  __              
 | | / (_) /  ___   __ _  ___   ___ _  / _/_ __/ /___ _________ 
 | |/ / / _ \/ -_) /  ' \/ -_) / _ `/ / _/ // / __/ // / __/ -_)
 |___/_/_.__/\__/ /_/_/_/\__/  \_,_/ /_/ \_,_/\__/\_,_/_/  \__/ 
                                                                
    """

st.set_page_config(
    page_title="你好悠扬",
    page_icon="🌼",
    layout="wide"
)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "我"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

st.title("Talk is cheap 🗨 Vibe me a future")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ 设置")
    
    selected_role = st.selectbox(
        "选择角色",
        ["悠扬"],
        index=0 if st.session_state.selected_role == "我" else 1
    )
    
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔗 JSONBin 配置")
    st.caption("用于同步消息到 Unity ChatDollKit（可选）")
    
    bin_id = st.text_input(
        "Bin ID",
        value=st.session_state.get("jsonbin_bin_id", ""),
        type="default",
        help="在 JSONBin.io 控制台获取你的 Bin ID"
    )
    st.session_state.jsonbin_bin_id = bin_id
    
    access_key = st.text_input(
        "Access Key",
        value=st.session_state.get("jsonbin_access_key", ""),
        type="password",
        help="在 JSONBin.io 控制台的 API Keys 页面获取"
    )
    st.session_state.jsonbin_access_key = access_key
    
    if bin_id and access_key:
        st.success("✅ JSONBin 已配置")
    else:
        st.warning("⚠️ 未配置 JSONBin，消息不会同步到 Unity")
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件\n"
        "- 配置 JSONBin 后，回复会同步到 Unity ChatDollKit\n"
        "- 在 JSONBin.io 注册账号并创建 Bin 后填入配置"
    )

if not st.session_state.initialized:
    role_prompt = get_role_prompt(st.session_state.selected_role)
    system_message = role_prompt + "\n\n" + get_break_rules()
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

st.code(get_portrait(), language=None)
st.markdown("---")

for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

if st.query_params.get("poll") == "true":
    bin_id = st.session_state.get("jsonbin_bin_id", "")
    access_key = st.session_state.get("jsonbin_access_key", "")
    result = get_latest_reply(bin_id, access_key)
    st.json(result)
    st.stop()

user_input = st.chat_input("输入你的消息...")

if user_input:
    if should_exit_by_user(user_input):
        st.info("对话已结束")
        st.stop()
    
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                role_prompt = get_role_prompt(st.session_state.selected_role)
                bin_id = st.session_state.get("jsonbin_bin_id", "")
                access_key = st.session_state.get("jsonbin_access_key", "")
                reply = chat_once(
                    st.session_state.conversation_history, 
                    user_input, 
                    role_prompt,
                    bin_id if bin_id else None,
                    access_key if access_key else None
                )
                
                st.write(reply)
                
                if should_exit_by_ai(reply):
                    st.info("对话已结束")
                    st.stop()
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.session_state.conversation_history.pop()
