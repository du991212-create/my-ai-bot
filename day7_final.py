import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re

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
    输入 B站 链接，返回视频的标题和简介 (防弹版)
    """
    # 1. 模拟浏览器 (防止被拦截)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    try:
        # allow_redirects=True 会自动处理 b23.tv 的跳转
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        # === 🛡️ 安全提取标题 (Safe Extraction) ===
        # 方案 A: 找 h1 标签 (电脑版常见)
        title_tag = soup.find('h1', class_="video-title")
        if title_tag:
            title = title_tag.get_text().strip()
        else:
            # 方案 B: 找 meta og:title (通用)
            meta_title = soup.find('meta', {"property": "og:title"})
            if meta_title:
                title = meta_title['content']
            else:
                # 方案 C: 实在找不到，就用网页标题
                title = soup.title.string if soup.title else "未知标题"

        # === 🛡️ 安全提取简介 ===
        # 尝试找 meta description
        meta_desc = soup.find('meta', {"name": "description"})
        if meta_desc:
            desc = meta_desc['content']
        else:
            # 备用：找 og:description
            og_desc = soup.find('meta', {"property": "og:description"})
            desc = og_desc['content'] if og_desc else "无法获取简介，请直接根据标题分析。"

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
    # === 🆕 新增：教程折叠面板 ===
    with st.expander("🤔 手机 B站 怎么复制链接？(点我看教程)"):
        st.write("跟着下图操作，只需 3 步：")

        # 把屏幕分成 3 列，并排显示图片
        col1, col2, col3 = st.columns(3)

        with col1:
            st.caption("1. 点击视频下方的分享箭头")
            st.image("step1.jpg", use_column_width=True)

        with col2:
            st.caption("2. 在菜单里找到“复制链接”")
            st.image("step2.jpg", use_column_width=True)

        with col3:
            st.caption("3. 提示“复制成功”即可粘贴")
            st.image("step3.jpg", use_column_width=True)

    # === 下面是原来的输入框 ===
    raw_input = st.text_input("请粘贴 Bilibili 视频链接 (直接粘，不用删中文):")
    # === 🎁 专属彩蛋：小井 ===
    # 修正：用列表 [] 把所有暗号包起来，然后用 in 来判断
    triggers = ["小井", "井飞玥", "大杜","杜覃", "我喜欢你"]

    if raw_input in triggers:
        st.snow()  # 1. 满屏飞气球 (或者换成 st.snow() 下雪)

        # 2. 弹出专属卡片
        st.success("✨ 捕捉到一只可爱的小井！")

        # 3. 写一段只有她能看见的话 (Markdown 格式)
        st.markdown("""
                <div style='color: #FF4B4B; font-size: 24px; font-weight: bold;'>
                    💖 To 小井：
                </div>

                <div style='font-size: 18px; line-height: 1.8; margin-top: 15px;'>
                    这个网站全世界都能用，<br>
                    <b>但这个彩蛋是为小井一人留的后门。</b>
                </div>

                <div style='text-align: right; font-size: 14px; color: gray; margin-top: 30px;'>
                    要好好吃午饭🌻！
                </div>
                """, unsafe_allow_html=True)

        # 4. (可选) 如果你有她的照片，可以取消下面这行的注释
        st.image("xiaojing.jpg")

        st.stop()  # 🛑 关键：让程序停在这里，不要去爬虫，防止报错
    if st.button("开始分析", key="btn_url"):
        if not raw_input:
            st.warning("请先粘贴内容！")
        else:
            # === 🆕 新增：智能提取 URL ===
            # 正则表达式的意思是：找 http 或 https 开头，直到遇到空格为止的一串字符
            match = re.search(r'(https?://\S+)', raw_input)

            if match:
                video_url = match.group(1)  # 提取到了干净的链接
                st.caption(f"🔍 已自动提取链接：{video_url}")  # 提示一下用户

                with st.spinner("正在爬取视频信息..."):
                    # 1. 调用爬虫函数 (用提取出来的 clean_url)
                    title, desc = get_bilibili_info(video_url)

                    if not title:
                        st.error(desc)
                    else:
                        st.success("爬取成功！")
                        st.write(f"**标题**：{title}")

                        # (下面的 AI 分析代码不用变，保持原样即可)
                        # ...
                        with st.spinner("AI 正在看简介..."):
                            # 把原来这里调用 client.chat... 的代码保留着
                            # ...
                            # 为了方便你复制，我把后面的一小段也贴在这里：
                            prompt = f"""
                            你是一个毒舌但专业的视频评论家。请根据以下视频标题和简介，分析这个视频讲了什么。
                            视频标题：{title}
                            视频简介：{desc}
                            请回答三个问题：
                            1. 🧐 **核心内容**：一句话概括它在讲什么？
                            2. 🎯 **适合人群**：谁应该看？谁没必要看？
                            3. ⭐ **推荐指数**：满分5星，你给几星？
                            """
                            response = client.chat.completions.create(
                                model=MY_MODEL_NAME,
                                messages=[
                                    {"role": "system", "content": "你是一个专业的视频内容分析师。"},
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            st.divider()
                            st.subheader("🤖 AI 分析报告")
                            st.markdown(response.choices[0].message.content)

            else:
                st.error("❌ 没在输入框里找到 http 链接，请检查一下粘贴的内容！")
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