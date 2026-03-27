# coding: utf-8

import uuid
import streamlit as st
from pandasai import Agent
from pandasai.schemas.df_config import Config
from pandasai.llm.openai import OpenAI


class LLMAgentHandler:
    agent_id: str
    llm_agent: Agent

    def __init__(self) -> None:
        self.llm_agent = None
        self.agent_id = str(uuid.uuid4())

    def _setup_llm(self):
        """设置 DeepSeek LLM（通过 OpenAI 兼容接口）"""
        # 优先从 session_state 获取（用户手动输入）
        api_key = st.session_state.get("api_key", "")
        base_url = st.session_state.get("model_base_url", "")
        
        # 如果 session_state 中没有，则从 secrets 获取
        if not api_key:
            api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        if not base_url:
            base_url = st.secrets.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        
        # 验证 API 密钥
        if not api_key:
            st.toast("请配置 API 密钥（在侧边栏输入或设置 Secrets）", icon="⚠️")
            return None
        
        try:
            # 使用 OpenAI 类连接 DeepSeek（兼容 OpenAI API）
            llm = OpenAI(
                api_token=api_key,
                api_base=base_url,
                model="deepseek-chat"
            )
            return llm
        except Exception as e:
            st.toast(f"LLM 初始化失败: {str(e)}", icon="❌")
            return None

    def configure_agent_with_data(self, dataframe, memory_limit):
        """配置 Agent 并加载数据"""
        llm = self._setup_llm()
        
        if llm is not None:
            try:
                # 配置 Agent 参数
                agent_config = Config(
                    llm=llm,
                    save_charts_path='exports/charts',
                    open_charts=False,
                    enable_cache=False,
                    verbose=True
                )
                
                # 创建 Agent
                self.llm_agent = Agent(
                    dfs=dataframe,
                    config=agent_config,
                    memory_size=memory_limit
                )
                
                st.session_state.llm_ready = True
                st.toast("✅ 语言模型初始化成功", icon="🎉")
                
            except Exception as e:
                st.toast(f"Agent 配置失败: {str(e)}", icon="❌")
                st.session_state.llm_ready = False
        else:
            st.session_state.llm_ready = False

    def submit_query(self, user_prompt):
        """提交用户查询"""
        if self.llm_agent is None:
            st.toast("语言模型未准备好，请检查配置", icon="❌")
            return "请先上传数据文件并确保 API 密钥配置正确"
        
        try:
            result = self.llm_agent.chat(user_prompt)
            return result
        except Exception as e:
            error_msg = str(e)
            # 处理 API 密钥错误
            if "401" in error_msg or "AuthenticationError" in error_msg:
                st.toast("API 密钥无效，请检查配置", icon="🔑")
                return "API 密钥认证失败，请检查密钥是否正确"
            elif "429" in error_msg:
                st.toast("请求频率过高，请稍后重试", icon="⏰")
                return "请求过于频繁，请稍后再试"
            else:
                st.toast(f"查询失败: {error_msg[:100]}", icon="❌")
                return f"分析出错: {error_msg}"

    def clear_conversation(self):
        """清除对话历史"""
        if self.llm_agent is not None:
            self.llm_agent.start_new_conversation()
        if "chat_history" in st.session_state:
            st.session_state.chat_history = []
