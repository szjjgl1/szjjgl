import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 配置matplotlib以确保中文显示
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.unicode_minus': False,
    'svg.fonttype': 'path',  # 使用路径渲染文本，不依赖系统字体
    'pdf.fonttype': 42,       # 确保PDF导出时字体正确
})

# 尝试多种字体配置
for font_config in [
    ['SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans'],
    ['Heiti TC', 'Microsoft YaHei', 'Arial Unicode MS'],
    ['Arial', 'sans-serif'],
]:
    try:
        plt.rcParams['font.sans-serif'] = font_config
        # 测试字体是否可用
        plt.figure()
        plt.text(0.5, 0.5, '测试中文显示', ha='center')
        plt.close()
        break  # 如果成功则退出循环
    except:
        continue  # 如果失败则尝试下一组字体

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

# 加载实际数据
@st.cache_data

def load_data():
    try:
        # 读取CSV文件
        df = pd.read_csv("1999-2023年数字化转型指数结果表.csv")
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

df_data = load_data()

# 创建企业字典
companies_dict = {}
if df_data is not None:
    # 提取所有唯一的股票代码和企业名称
    unique_companies = df_data[['股票代码', '企业名称']].drop_duplicates()
    for _, row in unique_companies.iterrows():
        stock_code = str(row['股票代码']).zfill(6)  # 确保股票代码是6位数字
        company_name = row['企业名称']
        companies_dict[stock_code] = company_name

# 创建侧边栏
st.sidebar.title("查询条件")
selection_method = st.sidebar.radio(
    "推荐方式:",
    ["输入股票代码", "选择股票代码"]
)

stock_code = None
if selection_method == "输入股票代码":
    stock_code = st.sidebar.text_input("输入股票代码:", value="000921")
    if stock_code:
        st.sidebar.markdown(f"您选择的股票代码：{stock_code}")
else:
    if companies_dict:
        selected_company = st.sidebar.selectbox(
            "选择企业:",
            list(companies_dict.keys()),
            format_func=lambda x: f"{x} - {companies_dict[x]}"
        )
        stock_code = selected_company
        st.sidebar.markdown(f"您选择的企业：{companies_dict[selected_company]}")
    else:
        st.sidebar.markdown("无企业数据可用")

# 显示选择结果
st.subheader("查询结果")
if stock_code and df_data is not None:
    # 格式化股票代码为6位数字
    formatted_stock_code = stock_code.zfill(6)
    
    # 查询该股票代码的所有数据
    company_data = df_data[df_data['股票代码'] == int(formatted_stock_code) if formatted_stock_code.isdigit() else formatted_stock_code]
    
    if not company_data.empty:
        # 获取企业名称
        company_name = company_data['企业名称'].iloc[0]
        st.markdown(f"正在查询股票代码 **{formatted_stock_code}** (**{company_name}**) 的数字化转型指数...")
        
        # 显示数据
        st.markdown("\n### 数字化转型指数数据")
        display_columns = ['年份', '数字化转型指数(0-100分)', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', '数字技术运用词频数']
        st.dataframe(company_data[display_columns], height=300)
        
        # 添加可视化
        st.markdown("\n### 数字化转型指数趋势")
        # 按年份排序
        company_data_sorted = company_data.sort_values('年份')
        
        # 使用Streamlit内置的line_chart函数，并确保正确设置索引和列名
        # 首先确保数据中的中文列名正确
        df_plot = company_data_sorted[['年份', '数字化转型指数(0-100分)']].copy()
        df_plot = df_plot.rename(columns={'数字化转型指数(0-100分)': '数字化转型指数'})
        
        # 绘制折线图
        st.subheader(f'{company_name} 数字化转型指数趋势')
        st.line_chart(
            data=df_plot.set_index('年份'),
            y_label='数字化转型指数(0-100分)',
            width=1000,
            height=500
        )
        
        # 添加额外的中文说明
        st.write("### 指数说明")
        st.write("数字化转型指数反映了企业在数字化转型方面的综合表现，范围为0-100分。")
        st.write("指数越高，表明企业的数字化转型程度越深。")
        
        # 显示统计信息
        st.markdown("\n### 统计信息")
        latest_year = company_data['年份'].max()
        latest_index = company_data[company_data['年份'] == latest_year]['数字化转型指数(0-100分)'].iloc[0]
        earliest_year = company_data['年份'].min()
        earliest_index = company_data[company_data['年份'] == earliest_year]['数字化转型指数(0-100分)'].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("最新年份", f"{latest_year}年")
        with col2:
            st.metric("最新指数", f"{latest_index:.2f}分")
        with col3:
            st.metric("指数变化", f"{latest_index - earliest_index:.2f}分")
    else:
        st.markdown(f"未找到股票代码 **{formatted_stock_code}** 的数据")

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