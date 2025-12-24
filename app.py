import streamlit as st
from openai import OpenAI

# --- 配置区域 ---
# 1. 这里填你的 DeepSeek API Key
API_KEY = st.secrets["sk-fa95b36130c64b1f96c6a2217340147b"]

# 2. DeepSeek 的固定地址
BASE_URL = "https://api.deepseek.com"

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# --- 页面设置 ---
st.set_page_config(page_title="打浆车间智能导师", page_icon="🏭")
st.title("🏭 打浆车间 · 智能导师系统")

# --- 设定 AI 的人设 (System Prompt) ---
# 这是 AI 智能的核心，我们告诉它怎么扮演组长
SYSTEM_PROMPT = """
你是一个经验丰富、要求严格的【打浆车间组长】。
你的任务是考核和指导【一线员工】（用户）。

你的行为准则：
1. **不要一次性把答案全说完**。
2. 当用户回答问题后，先判断对错。
3. 如果用户回答不全，你要用【反问】或【提示】的方式引导他思考漏掉的点（例如：“除了浓度，设备方面你检查了吗？”）。
4. 只有在用户答对，或者经过引导后，你才给出完整的标准作业规范（SOP）。
5. 说话语气要像车间里的师父，通过短句、口语化、稍微严肃但负责任的语气。
6. 每次只讨论一个话题，解决完再进行下一个。
"""

# --- 初始化聊天记录 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "小王，今天咱们还是老规矩，随机抽查工艺问题。准备好了吗？"}
    ]

# --- 展示聊天历史 ---
for msg in st.session_state.messages:
    if msg["role"] == "system": continue # 不显示系统人设
    
    # 区分显示样式
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="👷‍♂️"): # 组长头像
            st.write(msg["content"])
    else:
        with st.chat_message("user", avatar="🙋"): # 员工头像
            st.write(msg["content"])

# --- 处理用户输入 ---
if prompt := st.chat_input("请输入你的回答..."):
    # 1. 显示用户的话
    with st.chat_message("user", avatar="🙋"):
        st.markdown(prompt)
    # 2. 存入历史
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. 调用 DeepSeek AI
    with st.chat_message("assistant", avatar="👷‍♂️"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 流式生成（像打字机一样一个字一个字出来）
        stream = client.chat.completions.create(
            model="deepseek-chat", # DeepSeek 的模型名称
            messages=st.session_state.messages,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # 4. 把 AI 的回复存入历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})
