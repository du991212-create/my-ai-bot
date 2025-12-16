import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# ================= 1. 配置区域 =================
# 尝试获取云端 Key，拿不到就用本地的
try:
    MY_API_KEY = st.secrets["deepseek_key"]
except:
    MY_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # 👈 本地运行时，填你的真实 Key

MY_BASE_URL = "https://api.deepseek.com"  # 或硅基流动地址
MY_MODEL_NAME = "deepseek-chat"

client = OpenAI(api_key=MY_API_KEY, base_url=MY_BASE_URL)


# ================= 2. 爬虫核心功能 (Day 2 复习) =================
def get_bilibili_info(url):
    """
    输入 B站 链接，返回视频的标题和简介
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'  # 防止乱码

        # 使用 BeautifulSoup 解析网页骨架
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取标题 (查找 <h1 class="video-title">)
        # 注意：B站的网页结构可能会变，如果爬不到，通常是 class 名变了
        title_tag = soup.find('h1', class_="video-title")
        if not title_tag:
            # 备用方案：直接找 meta 标签
            title = soup.find('meta', {"property": "og:title"})['content']
        else:
            title = title_tag.get_text().strip()

        # 提取简介 (查找 <meta name="description">)
        desc = soup.find('meta', {"name": "description"})['content']

        return title, desc

    except Exception as e:
        return None, f"爬取失败: {e}"


# ================= 3. 网页界面 (Day 4 复习) =================
st.set_page_config(page_title="B站省流神器", page_icon="📺")
st.title("📺 B站视频 AI 省流助手")
st.markdown("输入视频链接，AI 帮你决定要不要看！")

# 创建两个选项卡：链接模式 / 文本模式
# (万一爬虫被反爬了，用户还能手动粘贴文本，这叫“鲁棒性”)
tab1, tab2 = st.tabs(["🔗 链接分析模式", "📝 文本粘贴模式"])

# --- 模式 A: 链接分析 ---
with tab1:
    video_url = st.text_input("请粘贴 Bilibili 视频链接 (比如 https://www.bilibili.com/video/BV1...):")

    if st.button("开始分析", key="btn_url"):
        if not video_url:
            st.warning("请先粘贴链接！")
        else:
            with st.spinner("正在爬取视频信息..."):
                # 1. 调用爬虫函数
                title, desc = get_bilibili_info(video_url)

                if not title:
                    st.error(desc)  # 显示爬虫报错信息
                else:
                    st.success("爬取成功！")
                    st.write(f"**标题**：{title}")
                    st.info(f"**简介预览**：{desc[:100]}...")

                    # 2. 调用 AI 分析 (Day 3 复习)
                    with st.spinner("AI 正在看简介..."):
                        prompt = f"""
                        你是一个毒舌但专业的视频评论家。请根据以下视频标题和简介，分析这个视频讲了什么。

                        视频标题：{title}
                        视频简介：{desc}

                        请回答三个问题：
                        1. 🧐 **核心内容**：一句话概括它在讲什么？
                        2. 🎯 **适合人群**：谁应该看？谁没必要看？
                        3. ⭐ **推荐指数**：满分5星，你给几星？（请根据内容的干货程度打分）
                        """

                        response = client.chat.completions.create(
                            model=MY_MODEL_NAME,
                            messages=[
                                {"role": "system", "content": "你是一个专业的视频内容分析师。"},
                                {"role": "user", "content": prompt}
                            ]
                        )

                        st.divider()  # 画一条分割线
                        st.subheader("🤖 AI 分析报告")
                        st.markdown(response.choices[0].message.content)

# --- 模式 B: 手动文本 ---
with tab2:
    st.write("如果你只有文字内容，或者爬虫失败了，可以用这个模式：")
    manual_text = st.text_area("把标题和简介粘在这里：", height=200)

    if st.button("开始分析", key="btn_text"):
        if manual_text:
            with st.spinner("AI 正在阅读..."):
                response = client.chat.completions.create(
                    model=MY_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "你是一个毒舌视频评论家。"},
                        {"role": "user", "content": f"请分析以下内容：\n{manual_text}"}
                    ]
                )
                st.subheader("🤖 AI 分析报告")
                st.markdown(response.choices[0].message.content)