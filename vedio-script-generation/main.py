import streamlit as st
from utils import generate_script

# 页面基础配置
st.set_page_config(page_title="视频脚本生成器", page_icon="🎬", layout="wide")

st.title("🎬 视频脚本生成器")

# 侧边栏配置（添加默认接口地址+提示）
with st.sidebar:
    st.header("🔑 阿里云百炼配置")
    bailian_api_key = st.text_input(
        "请输入阿里云百炼 API Key：",
        type="password",
        help="API Key可在阿里云百炼控制台获取：https://dashscope.console.aliyun.com/apiKey"
    )
    # 设置默认接口地址，减少用户输入成本
    default_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    bailian_endpoint = st.text_input(
        "请输入阿里云百炼接口地址：",
        value=default_endpoint,
        help="默认使用阿里云官方地址，无需修改（海外用户可换地域地址）"
    )
    # 添加使用说明
    st.markdown("""
    ### 📌 使用说明
    1. API Key 需从阿里云百炼控制台获取
    2. 接口地址默认即可，无需修改
    3. 创造力值越大，脚本越有创意（0-1）
    """)

# 主界面输入项
col1, col2 = st.columns([2, 1])
with col1:
    subject = st.text_input(
        "💡 请输入视频的主题",
        placeholder="例如：Sora模型、AI绘画教程、Python入门..."
    )
with col2:
    video_length = st.number_input(
        "⏱️ 视频时长（分钟）",
        min_value=0.1,
        step=0.1,
        value=1.0,
        help="建议0.5-3分钟，适配短视频场景"
    )

creativity = st.slider(
    "✨ 脚本创造力（0=严谨，1=多样）",
    min_value=0.0,
    max_value=1.0,
    value=0.5,  # 调整默认值更适中
    step=0.1,
    help="数值越小，内容越贴合事实；数值越大，内容越有创意"
)

submit = st.button("🚀 生成脚本", type="primary")

# 输入校验
if submit:
    # 1. 校验API Key和接口地址
    if not bailian_api_key.strip():
        st.error("❌ 请输入有效的阿里云百炼 API Key")
        st.stop()
    if not bailian_endpoint.strip():
        st.error("❌ 请输入有效的阿里云百炼接口地址")
        st.stop()

    # 2. 校验主题
    if not subject.strip():
        st.error("❌ 请输入视频主题（不能为空）")
        st.stop()

    # 3. 校验时长
    if video_length < 0.1:
        st.error("❌ 视频时长不能小于0.1分钟")
        st.stop()

    # 4. 调用生成函数（添加异常处理）
    try:
        with st.spinner("🤖 AI正在思考中，请稍等..."):
            search_result, title, script = generate_script(
                subject=subject,
                video_length=video_length,
                creativity=creativity,
                bailian_api_key=bailian_api_key,
                bailian_endpoint=bailian_endpoint
            )

        # 展示结果
        st.success("✅ 视频脚本生成成功！")

        # 标题展示（突出显示）
        st.subheader("🔥 视频标题：")
        st.write(title)

        # 脚本展示（带分隔线）
        st.subheader("📝 视频脚本：")
        # 按【开头、中间、结尾】拆分展示（优化排版）
        script_parts = script.split("【")
        for part in script_parts:
            if part.strip():
                if "开头】" in part:
                    st.markdown("### 🎬 开头")
                    st.write(part.replace("开头】", "").strip())
                elif "中间】" in part:
                    st.markdown("### 📖 中间（干货）")
                    st.write(part.replace("中间】", "").strip())
                elif "结尾】" in part:
                    st.markdown("### 🎉 结尾（惊喜）")
                    st.write(part.replace("结尾】", "").strip())

        # 维基百科搜索结果（折叠展示）
        with st.expander("📚 维基百科参考资料（点击展开）", expanded=False):
            if search_result:
                st.info(search_result)
            else:
                st.warning("未找到相关维基百科信息")

    except Exception as e:
        st.error(f"❌ 生成失败：{str(e)}")
