# Streamlit主应用入口文件
# 该文件用于将Streamlit Cloud的请求转发到实际的应用文件

import streamlit as st
import importlib
import os

# 导入实际的应用文件
try:
    from digital_transformation_dashboard import main
    
    # 运行应用
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error(f"应用加载失败: {str(e)}")
    st.write("正在尝试直接运行应用...")
    
    # 尝试直接运行应用文件
    try:
        exec(open("digital_transformation_dashboard.py").read())
    except Exception as ex:
        st.error(f"直接运行也失败了: {str(ex)}")