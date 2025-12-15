import streamlit as st
from openai import OpenAI

# ==============================================
# 1. 你的配置区域 (⚠️请一定要把你的 Key 填在下面引号里！)
# ==============================================
MY_API_KEY = st.secrets["deepseek_key"]
# MY_API_KEY = "sk-03f0aab8b93947628af3b5da6b13b96a"  # 👈 这里填你的 Key
MY_BASE_URL = "https://api.deepseek.com"  # 如果是 DeepSeek 就填这个
MY_MODEL_NAME = "deepseek-chat"
# ==============================================

# 初始化 AI 客户端
client = OpenAI(
    api_key=MY_API_KEY,
    base_url=MY_BASE_URL,
)

# === 网页界面开始 ===

# 1. 标题
st.title("💬 大杜什么都想知道")
st.image("app123.jpg", width=150)
# 2. 侧边栏：设置人设
st.sidebar.header("⚙️ 操控大杜")
persona = st.sidebar.text_input("给 大杜 设定一个人设", value="有个姑娘叫小井，现在你已经深深喜欢上了她")

# 3. 主界面：聊天输入框 (这正是你在找的！)
# 我们用一个“表单”把输入框和按钮包起来
with st.form("my_form"):
    st.write("请在下方输入你的问题：")
    # text_area 是一个大的文本输入框
    user_msg = st.text_area("User Input", height=100, placeholder="比如：帮我写个喜欢小井的理由")

    # submit_button 是提交按钮
    submitted = st.form_submit_button("🚀说给大杜听")

# === 处理逻辑 ===
# 当你点击了“发送”按钮，并且输入框里有字时，才会运行下面的代码
if submitted and user_msg:
    # A. 在界面上显示你问了什么
    st.info(f"你问：{user_msg}")

    # B. 调用 AI
    with st.spinner("大杜 正在思考中..."):
        try:
            # 发送请求
            response = client.chat.completions.create(
                model=MY_MODEL_NAME,
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": user_msg}
                ]
            )
            answer = response.choices[0].message.content

            # C. 显示结果
            st.success("大杜 回答：")
            st.markdown(answer)

        except Exception as e:
            st.error(f"出错了: {e}")