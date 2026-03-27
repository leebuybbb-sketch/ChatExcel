# coding: utf-8

import os
import io
import uuid
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
import matplotlib
import streamlit as st

from pandasai import SmartDataframe
from pandasai.helpers import Logger

from llm_agent import LLMAgentHandler

# 创建必要的目录
os.makedirs('exports/charts', exist_ok=True)
os.makedirs('.matplotlib', exist_ok=True)

# 缓存LLM代理实例
@st.cache_resource
def get_llm_agent(agent_id: str) -> LLMAgentHandler:
    return LLMAgentHandler()

# 页面配置 - 作为第一个Streamlit命令
st.set_page_config(
    page_title="智能表格分析平台",
    layout="wide",
    page_icon="📊"
)

# ========== 从 Secrets 自动填充配置 ==========
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.session_state.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
if "model_base_url" not in st.session_state or not st.session_state.model_base_url:
    st.session_state.model_base_url = st.secrets.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")
if "last_model_choice" not in st.session_state:
    st.session_state.last_model_choice = "DeepSeek"
if "last_memory_limit" not in st.session_state:
    st.session_state.last_memory_limit = 10
if "agent_identifier" not in st.session_state:
    st.session_state.agent_identifier = str(uuid.uuid4())
# ============================================

# 自定义CSS样式 - 调整字体大小和整体布局
st.markdown("""
<style>
    .main-header {
        color: #2c3e50;
        font-size: 1.8rem;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #34495e;
        font-size: 1.2rem;
        border-left: 4px solid #3498db;
        padding-left: 0.75rem;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.4rem 0.8rem;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 6px;
        border: 1px solid #bdc3c7;
        font-size: 0.9rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .user-message, .assistant-message {
        padding: 0.6rem;
        margin: 0.4rem 0;
        max-width: 80%;
        font-size: 0.9rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-radius: 10px 10px 10px 0;
        align-self: flex-end;
    }
    .assistant-message {
        background-color: #ffffff;
        border-radius: 10px 10px 0 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #f5f7fa;
    }
    .stMarkdown p {
        font-size: 0.95rem;
    }
    .stInfo, .stSuccess, .stError {
        font-size: 0.9rem;
        padding: 0.6rem;
    }
    .stTabLabel {
        font-size: 0.95rem;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化日志和 matplotlib 配置
logger = Logger()
if os.path.exists("./.matplotlib/.matplotlibrc"):
    matplotlib.rc_file("./.matplotlib/.matplotlibrc")

# 顶部标题区域
col_title, col_logo = st.columns([8, 1])
with col_title:
    st.markdown("<h1 class='main-header'>智能表格分析平台</h1>", unsafe_allow_html=True)
    st.markdown("基于先进语言模型的数据分析工具，轻松挖掘表格数据价值")

# 主内容区与侧边栏布局调整
main_content, sidebar = st.columns([3, 1])

# 会话状态初始化
CHAT_HISTORY_KEY = "chat_records"
if CHAT_HISTORY_KEY not in st.session_state:
    st.session_state[CHAT_HISTORY_KEY] = []

if "llm_ready" not in st.session_state:
    st.session_state.llm_ready = False

# 主内容区域
with main_content:
    # 数据展示与聊天区域分为上下两部分
    data_section, chat_section = st.tabs(["📋 数据预览", "💬 分析对话"])

    with data_section:
        st.markdown("<h3 class='sub-header'>数据详情预览</h3>", unsafe_allow_html=True)
        dataframe_display = st.dataframe(pd.DataFrame(), use_container_width=True)
        record_counter = st.info("等待数据上传...")

    with chat_section:
        st.markdown("<h3 class='sub-header'>分析对话</h3>", unsafe_allow_html=True)

        # 聊天历史展示区域
        chat_container = st.container()
        with chat_container:
            for message in st.session_state[CHAT_HISTORY_KEY]:
                if message["role"] == "user":
                    st.markdown(f"<div class='user-message'><strong>你:</strong> {message['content']}</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='assistant-message'><strong>分析助手:</strong> {message['content']}</div>",
                                unsafe_allow_html=True)
                    # 处理特殊类型消息
                    if "type" in message:
                        if message["type"] == "plot":
                            st.image(message['content'], use_column_width=True)
                        elif message["type"] == "dataframe":
                            st.dataframe(message['data'], use_container_width=True)

        # 用户输入区域
        user_input = st.chat_input("请输入您的分析问题，例如：'分析各地区销售额并绘图'")
        if user_input is not None:
            # 添加用户消息到历史
            st.session_state[CHAT_HISTORY_KEY].append({
                "role": "user",
                "content": user_input
            })

            # 显示用户消息
            with chat_container:
                st.markdown(f"<div class='user-message'><strong>你:</strong> {user_input}</div>", unsafe_allow_html=True)

            # 生成回复
            with chat_container:
                if not st.session_state.llm_ready:
                    response_text = "请先上传文件并完成LLM配置"
                    st.markdown(f"<div class='assistant-message'><strong>分析助手:</strong> {response_text}</div>",
                                unsafe_allow_html=True)
                    st.session_state[CHAT_HISTORY_KEY].append({
                        "role": "assistant",
                        "content": response_text
                    })
                else:
                    # 显示加载状态
                    progress_indicator = st.markdown(
                        f"<div class='assistant-message'><strong>分析助手:</strong> 正在分析，请稍候...</div>",
                        unsafe_allow_html=True)

                    # 获取分析结果
                    agent = get_llm_agent(st.session_state.agent_identifier)
                    analysis_result = agent.submit_query(user_input)

                    # 处理不同类型的结果
                    if isinstance(analysis_result, (SmartDataframe, pd.DataFrame)):
                        # 处理数据框结果
                        df_result = analysis_result.dataframe if isinstance(analysis_result,
                                                                            SmartDataframe) else analysis_result
                        progress_indicator.empty()
                        st.markdown(f"<div class='assistant-message'><strong>分析助手:</strong> 数据分析结果如下</div>",
                                    unsafe_allow_html=True)
                        st.dataframe(df_result, use_container_width=True)
                        st.session_state[CHAT_HISTORY_KEY].append({
                            "role": "assistant",
                            "content": "数据分析结果如下",
                            "type": "dataframe",
                            "data": df_result
                        })

                    elif isinstance(analysis_result, Dict) and "type" in analysis_result and analysis_result[
                        "type"] == "plot":
                        # 处理图表结果
                        chart_path = analysis_result['value']
                        if os.path.isfile(chart_path) and os.path.exists(chart_path):
                            unique_id = str(uuid.uuid4()).replace("-", "")
                            new_chart_path = chart_path.replace('.png', f'{unique_id}.png')
                            os.rename(chart_path, new_chart_path)
                            progress_indicator.empty()
                            st.markdown(f"<div class='assistant-message'><strong>分析助手:</strong> 数据可视化结果如下</div>",
                                        unsafe_allow_html=True)
                            st.image(new_chart_path, use_column_width=True)
                            st.session_state[CHAT_HISTORY_KEY].append({
                                "role": "assistant",
                                "content": "数据可视化结果如下",
                                "type": "plot",
                                "data": new_chart_path
                            })

                    elif '.png' in str(analysis_result):
                        # 处理图片路径结果
                        chart_base_dir = 'exports/charts'
                        temp_chart_path = os.path.join(chart_base_dir, 'temp_chart.png')
                        if os.path.isfile(temp_chart_path) and os.path.exists(temp_chart_path):
                            unique_id = str(uuid.uuid4()).replace("-", "")
                            new_chart_path = temp_chart_path.replace('.png', f'{unique_id}.png')
                            os.rename(temp_chart_path, new_chart_path)
                            progress_indicator.empty()
                            st.markdown(f"<div class='assistant-message'><strong>分析助手:</strong> 数据可视化结果如下</div>",
                                        unsafe_allow_html=True)
                            st.image(new_chart_path, use_column_width=True)
                            st.session_state[CHAT_HISTORY_KEY].append({
                                "role": "assistant",
                                "content": "数据可视化结果如下",
                                "type": "plot",
                                "data": new_chart_path
                            })

                    else:
                        # 处理文本结果
                        progress_indicator.empty()
                        st.markdown(
                            f"<div class='assistant-message'><strong>分析助手:</strong> {str(analysis_result)}</div>",
                            unsafe_allow_html=True)
                        st.session_state[CHAT_HISTORY_KEY].append({
                            "role": "assistant",
                            "content": str(analysis_result)
                        })

# 侧边栏配置区域
with sidebar:
    st.markdown("<h3 class='sub-header'>系统配置</h3>", unsafe_allow_html=True)

    # 模型配置卡片
    with st.expander("🤖 模型设置", expanded=True):
        model_choice = st.selectbox("选择语言模型", ["DeepSeek"])

        # 模型参数配置
        if model_choice == "DeepSeek":
            # 显示密钥状态
            if st.session_state.api_key:
                st.info("✅ API 密钥已配置（来自 Secrets）")
            else:
                st.warning("⚠️ 请在 Secrets 中配置 DEEPSEEK_API_KEY")
            
            api_key = st.text_input(
                "API 密钥（可修改）",
                st.session_state.api_key,
                type="password",
                placeholder="请输入API密钥"
            )
            base_url = st.text_input(
                "接口地址",
                st.session_state.model_base_url,
                placeholder="https://api.deepseek.com"
            )

        # 记忆长度配置
        memory_limit = st.selectbox(
            "对话记忆长度",
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            index=9
        )

    # 对话管理卡片
    with st.expander("💬 对话管理", expanded=True):
        if st.button("+ 新建对话"):
            st.session_state.llm_ready = False
            st.session_state[CHAT_HISTORY_KEY] = []
            st.success("已创建新对话")

        # 配置验证信息
        config_status = st.empty()
        if model_choice == "DeepSeek":
            if not api_key:
                config_status.error("请输入有效的API密钥")
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                st.session_state.llm_ready = False

            if not base_url:
                config_status.error("请输入有效的接口地址")
            if base_url != st.session_state.model_base_url:
                st.session_state.model_base_url = base_url
                st.session_state.llm_ready = False

    # 模型选择变更处理
    if model_choice != st.session_state.last_model_choice:
        st.session_state.last_model_choice = model_choice
        st.session_state.llm_ready = False

    # 记忆长度变更处理
    if memory_limit != st.session_state.last_memory_limit:
        st.session_state.last_memory_limit = memory_limit
        st.session_state.llm_ready = False

    st.divider()

    # 文件上传区域
    st.markdown("<h3 class='sub-header'>数据上传</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("选择Excel或CSV文件", type=["xlsx", "xls", "csv"])

    if uploaded_file is None:
        st.session_state.file_uploaded = False
        if st.session_state.llm_ready and "agent_identifier" in st.session_state:
            get_llm_agent(st.session_state.agent_identifier).clear_conversation()
        st.info("请上传数据文件开始分析")
    else:
        # 处理上传的文件
        file_content = io.BytesIO(uploaded_file.getvalue())
        file_extension = Path(uploaded_file.name).suffix.lower()

        # 读取文件内容
        if file_extension == ".csv":
            data_frame = pd.read_csv(file_content, encoding='utf-8')
        else:
            data_frame = pd.read_excel(file_content)

        # 更新数据展示
        dataframe_display.dataframe(data_frame)
        record_counter.info(f"共 {len(data_frame)} 条记录")
        st.success(f"已上传: {uploaded_file.name}")

        # 检查文件是否变更或LLM未就绪
        if "last_uploaded_file" not in st.session_state:
            st.session_state.last_uploaded_file = None

        if uploaded_file != st.session_state.last_uploaded_file or not st.session_state.llm_ready:
            st.session_state.agent_identifier = str(uuid.uuid4())
            get_llm_agent(st.session_state.agent_identifier).configure_agent_with_data(
                data_frame, memory_limit
            )

        st.session_state.last_uploaded_file = uploaded_file

# 日志记录LLM就绪状态
logger.log(f"LLM就绪状态: {st.session_state.llm_ready}", level=logging.INFO)

# 重置Agent ID当LLM未就绪时
if not st.session_state.llm_ready:
    st.session_state.agent_identifier = str(uuid.uuid4())
