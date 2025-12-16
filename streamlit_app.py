# Streamlit主应用入口文件
# 该文件用于将Streamlit Cloud的请求转发到实际的应用文件

import streamlit as st
import os

# 直接运行实际的应用文件
try:
    exec(open("digital_transformation_dashboard.py").read())
except Exception as e:
    st.error(f"应用加载失败: {str(e)}")