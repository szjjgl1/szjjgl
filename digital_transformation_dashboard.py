import streamlit as st
import pandas as pd
import numpy as np

# 设置页面配置
st.set_page_config(
    page_title="企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
)

# 应用标题和信息
st.title("企业数字化转型指数查询系统")
st.markdown("**版本：2024.01.15更新**")
st.markdown("**数据源：** 1999-2023年企业年报")
st.markdown("**数据更新时间：** 2023年12月")
st.markdown("**系统说明：** 本系统基于企业年报文本分析构建数字化转型指数")

# 添加示例数据和简单功能
example_companies = {
    "000021": "深科技",
    "600000": "浦发银行",
    "000001": "平安银行",
    "000002": "万科A",
    "600519": "贵州茅台",
    "000858": "五粮液"
}

# 创建侧边栏
st.sidebar.title("查询条件")
selection_method = st.sidebar.radio(
    "推荐方式:",
    ["输入股票代码", "选择股票代码"]
)

if selection_method == "输入股票代码":
    stock_code = st.sidebar.text_input("输入股票代码:", value="000021")
    if stock_code:
        st.sidebar.markdown(f"您选择的股票代码：{stock_code}")
else:
    selected_company = st.sidebar.selectbox(
        "选择示例企业:",
        list(example_companies.keys()),
        format_func=lambda x: f"{x} - {example_companies[x]}"
    )
    stock_code = selected_company
    st.sidebar.markdown(f"您选择的企业：{example_companies[selected_company]}")

# 显示选择结果
st.subheader("查询结果")
if stock_code:
    st.markdown(f"正在查询股票代码 **{stock_code}** 的数字化转型指数...")
    # 这里可以添加实际的数据查询逻辑
    st.markdown("\n### 示例数据")
    sample_data = {
        "年份": [2019, 2020, 2021, 2022, 2023],
        "数字化转型指数": [0.35, 0.42, 0.48, 0.55, 0.62]
    }
    df = pd.DataFrame(sample_data)
    st.dataframe(df)
    
    # 添加简单的可视化
    st.markdown("\n### 数字化转型指数趋势")
    st.line_chart(df.set_index("年份"))

# 添加应用说明
st.markdown("\n---")
st.subheader("应用说明")
st.markdown("1. 本系统基于企业年报文本分析构建数字化转型指数")
st.markdown("2. 支持通过股票代码查询企业的数字化转型指数")
st.markdown("3. 提供指数趋势可视化功能")
st.markdown("4. 数据覆盖1999-2023年的企业年报数据")

# 定义main函数，确保Streamlit Cloud能正确导入和运行
if __name__ == "__main__":
    pass

# 添加main函数定义，确保Streamlit Cloud能正确导入
def main():
    pass