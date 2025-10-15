# coding: utf-8

import uuid
from pandasai import Agent
from pandasai.schemas.df_config import Config
from pandasai.llm.openai import OpenAI
import streamlit as st


class LLMAgentHandler:
    agent_id: str
    llm_agent: Agent

    def __init__(self) -> None:
        self.llm_agent = None
        self.agent_id = str(uuid.uuid4())

    def _create_deepseek_client(self, api_key, base_url):
        # 添加DeepSeek模型支持
        OpenAI._supported_chat_models.append('deepseek-chat')
        return OpenAI(
            api_token=api_key,
            api_base=base_url,
            model='deepseek-chat'
        )

    def _setup_llm(self):
        selected_model = st.session_state.last_model_choice
        llm_instance = None
        
        if selected_model == "DeepSeek":
            if st.session_state.api_key != "":
                llm_instance = self._create_deepseek_client(
                    st.session_state.api_key,
                    st.session_state.model_base_url
                )
        
        if llm_instance is None:
            st.toast("语言模型初始化失败，请检查配置参数", icon="⚠️")
        return llm_instance

    def configure_agent_with_data(self, dataframe, memory_limit):
        llm = self._setup_llm()
        if llm is not None:
            # 配置Agent参数
            agent_config = Config(
                llm=llm,
                save_charts_path='exports/charts',
                open_charts=False,
                enable_cache=False,
                verbose=True
            )
            self.llm_agent = Agent(
                dfs=dataframe,
                config=agent_config,
                memory_size=memory_limit
            )
            st.session_state.llm_ready = True

    def submit_query(self, user_prompt):
        if self.llm_agent is None:
            st.toast("语言模型未准备好，请检查配置", icon="❌")
            st.stop()
        return self.llm_agent.chat(user_prompt)

    def clear_conversation(self):
        self.llm_agent.start_new_conversation()
        st.session_state.chat_history = []
