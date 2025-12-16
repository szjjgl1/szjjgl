# 直接复制digital_transformation_dashboard.py的内容到streamlit_app.py

# 先导入基础库
import pandas as pd
import numpy as np
import os
import sys
import subprocess
from datetime import datetime

# 尝试导入streamlit
streamlit_available = False
try:
    import streamlit as st
    streamlit_available = True
except ImportError:
    streamlit_available = False

# 尝试导入可视化库
matplotlib_available = False
try:
    import matplotlib
    # 先设置matplotlib后端
    matplotlib.use('Agg')  # 使用Agg后端，更适合服务器环境
    import matplotlib.pyplot as plt
    
    # 在Streamlit Cloud环境中，使用路径渲染确保中文显示
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['svg.fonttype'] = 'path'  # 关键：将文本渲染为路径，不依赖系统字体
    plt.rcParams['pdf.fonttype'] = 42  # 解决PDF中文字体问题
    plt.rcParams['font.size'] = 10  # 设置默认字体大小
    plt.rcParams['text.usetex'] = False  # 禁用LaTeX渲染
    
    # 导入cmap工具，用于处理颜色映射
    from matplotlib import cm
    
    matplotlib_available = True
except ImportError:
    matplotlib_available = False

seaborn_available = False
try:
    import seaborn as sns
    seaborn_available = True
except ImportError:
    seaborn_available = False

# 设置中文字体支持
if matplotlib_available:
    # 尝试多种中文字体，确保在不同环境下都能正常显示
    plt.rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans', 
                                  'WenQuanYi Micro Hei', 'Heiti TC', 'NSimSun', 'SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['svg.fonttype'] = 'none'  # 解决SVG中文字体问题
    plt.rcParams['pdf.fonttype'] = 42  # 解决PDF中文字体问题
    plt.rcParams['font.size'] = 10  # 设置默认字体大小
    plt.rcParams['axes.titlesize'] = 12  # 设置标题字体大小
    plt.rcParams['axes.labelsize'] = 11  # 设置坐标轴标签字体大小

# 应用标题和简介
if streamlit_available:
    st.set_page_config(
        page_title="企业数字化转型指数查询系统",
        page_icon="📊",
        layout="wide"
    )
    
    # 注入CSS加载在线中文字体（Google Fonts）
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
    
    body {
        font-family: 'Noto Sans SC', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title('企业数字化转型指数查询系统')
    st.write('根据1999-2023年数据，通过股票代码查询企业数字化转型指数及历年趋势')

# 获取CSV文件路径
file_path = '1999-2023年数字化转型指数结果表.csv'

# 检查文件是否存在
if os.path.exists(file_path):
    # 读取CSV文件（只读取前20000行以提高性能）
    @st.cache_data
    def load_data():
        # 使用chunksize分批读取以避免内存问题
        chunks = []
        # 将股票代码列指定为字符串类型读取，避免类型转换问题
        for chunk in pd.read_csv(file_path, chunksize=10000, dtype={'股票代码': str}):
            chunks.append(chunk)
        return pd.concat(chunks)
    
    try:
        # 加载数据
        df = load_data()
        
        # 获取所有股票代码和企业名称的映射字典
        # 确保股票代码是字符串类型
        df['股票代码'] = df['股票代码'].astype(str)
        # 去除可能的前导/尾随空格
        df['股票代码'] = df['股票代码'].str.strip()
        
        # 创建唯一的股票代码-企业名称映射（取每个股票代码的第一个企业名称）
        stock_company_map = {}
        for idx, row in df.iterrows():
            stock_code = row['股票代码']
            if stock_code not in stock_company_map:
                stock_company_map[stock_code] = row['企业名称']
        
        unique_stocks = list(stock_company_map.keys())
        unique_stocks.sort()  # 排序以便更好地浏览
        
        # 创建股票代码输入框
        st.sidebar.header('查询条件')
        search_option = st.sidebar.radio(
            "搜索方式：",
            ('输入股票代码', '选择股票代码')
        )
        
        selected_stock = None
        
        if search_option == '输入股票代码':
            stock_input = st.sidebar.text_input('请输入股票代码（如：000921）', '')
            if stock_input:
                # 去除输入的空格
                stock_input = stock_input.strip()
                
                # 标准化股票代码格式（补零到6位）
                try:
                    # 尝试转换为整数再格式化为6位字符串
                    stock_input = f"{int(stock_input):06d}"
                except ValueError:
                    # 如果不是数字，保持原样
                    pass
                
                # 首先直接查找
                if stock_input in stock_company_map:
                    selected_stock = stock_input
                    st.sidebar.success(f"找到企业：{stock_company_map[stock_input]}")
                else:
                    # 尝试不同格式的匹配
                    found = False
                    
                    # 1. 尝试部分匹配
                    for code in stock_company_map.keys():
                        if stock_input in code or code in stock_input:
                            selected_stock = code
                            st.sidebar.success(f"找到匹配企业：{stock_company_map[code]} (股票代码：{code})")
                            found = True
                            break
                    
                    # 2. 尝试去除可能的前缀（如SZ、SH）
                    if not found:
                        if len(stock_input) > 6:
                            # 尝试只取后6位
                            suffix = stock_input[-6:]
                            if suffix in stock_company_map:
                                selected_stock = suffix
                                st.sidebar.success(f"找到企业：{stock_company_map[suffix]}")
                                found = True
                    
                    if not found:
                        st.sidebar.error(f"未找到股票代码：{stock_input}")
                        # 显示一些示例股票代码供参考
                        st.sidebar.info(f"示例股票代码：{list(stock_company_map.keys())[:5]}")
        else:
            # 提供股票代码下拉选择，按每100个分组以提高性能
            stock_groups = [unique_stocks[i:i+100] for i in range(0, len(unique_stocks), 100)]
            group_index = st.sidebar.selectbox(
                '选择股票代码分组',
                range(len(stock_groups)),
                format_func=lambda x: f"分组 {x+1}: {stock_groups[x][0]} - {stock_groups[x][-1]}"
            )
            selected_group = stock_groups[group_index]
            
            # 创建股票代码-企业名称字典用于显示
            display_dict = {f"{code} - {stock_company_map[code]}": code for code in selected_group}
            display_options = list(display_dict.keys())
            
            selected_display = st.sidebar.selectbox(
                '选择企业',
                display_options
            )
            
            if selected_display:
                selected_stock = display_dict[selected_display]
        
        # 如果选择了股票代码
        if selected_stock:
            # 筛选数据
            company_data = df[df['股票代码'] == selected_stock].sort_values('年份')
            company_name = company_data['企业名称'].iloc[0] if not company_data.empty else '未知'
            
            # 显示企业基本信息
            st.header(f"{company_name} ({selected_stock}) 数字化转型指数")
            
            if not company_data.empty:
                # 创建年份选择器，选择特定年份查看详细数据
                years = sorted(company_data['年份'].unique())
                selected_year = st.selectbox('选择年份查看详细数据：', years, index=len(years)-1)
                
                # 获取选定年份的数据
                year_data = company_data[company_data['年份'] == selected_year].iloc[0]
                
                # 显示选定年份的详细信息
                st.subheader(f"{selected_year}年详细数据")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("数字化转型指数", f"{year_data['数字化转型指数(0-100分)']:.2f}分")
                    st.metric("人工智能词频数", year_data['人工智能词频数'])
                    st.metric("大数据词频数", year_data['大数据词频数'])
                with col2:
                    st.metric("云计算词频数", year_data['云计算词频数'])
                    st.metric("区块链词频数", year_data['区块链词频数'])
                
                # 绘制历年数字化转型指数折线图
                if matplotlib_available:
                    st.subheader('历年数字化转型指数趋势')
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(company_data['年份'], company_data['数字化转型指数(0-100分)'], marker='o', linewidth=2, markersize=5, color='#1f77b4')
                    ax.set_xlabel('年份', fontsize=12)
                    ax.set_ylabel('数字化转型指数(0-100分)', fontsize=12)
                    ax.set_title('历年数字化转型指数趋势', fontsize=14)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.tick_params(axis='x', rotation=45)
                    
                    # 自动设置x轴刻度
                    years = company_data['年份'].unique()
                    if len(years) > 20:
                        step = len(years) // 10
                        ax.set_xticks(years[::step])
                    
                    st.pyplot(fig)
                    plt.close(fig)
                
                # 绘制数字技术维度雷达图
                if matplotlib_available and seaborn_available:
                    st.subheader('数字技术维度分析')
                    
                    # 提取数字技术相关指标
                    tech_columns = ['人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数']
                    tech_data = year_data[tech_columns].tolist()
                    
                    # 计算角度
                    num_vars = len(tech_columns)
                    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
                    
                    # 闭合雷达图
                    tech_data += tech_data[:1]
                    angles += angles[:1]
                    
                    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
                    ax.plot(angles, tech_data, linewidth=2, linestyle='solid', label='2023年')
                    ax.fill(angles, tech_data, alpha=0.25)
                    
                    # 设置标签
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(tech_columns, fontsize=10)
                    
                    # 设置标题
                    ax.set_title('数字技术维度雷达图', fontsize=14, pad=20)
                    
                    # 添加图例
                    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
                    
                    st.pyplot(fig)
                    plt.close(fig)
            else:
                st.warning(f"未找到 {selected_stock} 的数据")
    except Exception as e:
        st.error(f"数据处理错误：{str(e)}")
        import traceback
        st.error(traceback.format_exc())
else:
    if streamlit_available:
        st.error(f"未找到数据文件：{file_path}")
        st.info("请确保数据文件与应用程序在同一目录下")

# 添加一些示例企业供用户参考
if streamlit_available and os.path.exists(file_path):
    st.sidebar.markdown("---")
    st.sidebar.subheader("示例企业")
    # 获取前10个企业作为示例
    if 'stock_company_map' in locals() and stock_company_map:
        example_companies = list(stock_company_map.items())[:10]
        for code, name in example_companies:
            st.sidebar.info(f"{code} - {name}")

# 添加页脚信息
if streamlit_available:
    st.markdown("---")
    st.markdown("**数据来源**：1999-2023年企业年报")
    st.markdown("**数据更新时间**：2023年12月")
    st.markdown("**系统说明**：本系统基于企业年报文本分析构建数字化转型指数", unsafe_allow_html=True)

# 定义main函数，确保Streamlit Cloud能正确导入和运行
if __name__ == "__main__":
    # 这个函数确保应用能作为脚本直接运行
    pass

# 添加main函数定义，确保Streamlit Cloud能正确导入
def main():
    # 应用代码已经在文件中直接执行，这里不需要额外的代码
    pass