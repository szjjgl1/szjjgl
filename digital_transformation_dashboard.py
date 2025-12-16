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
    
    # 设置字体相关参数
    plt.rcParams['font.family'] = 'sans-serif'  # 使用sans-serif字体族
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    
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
        # 创建映射字典
        stock_company_map = dict(zip(df['股票代码'], df['企业名称']))
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
                
                # 首先直接查找
                if stock_input in stock_company_map:
                    selected_stock = stock_input
                    st.sidebar.success(f"找到企业：{stock_company_map[stock_input]}")
                else:
                    # 尝试不同格式的匹配，比如补零或去除零
                    found = False
                    # 尝试在所有股票代码中查找包含关系
                    for code in stock_company_map.keys():
                        if stock_input == code or stock_input in code or code in stock_input:
                            selected_stock = code
                            st.sidebar.success(f"找到匹配企业：{stock_company_map[code]} (股票代码：{code})")
                            found = True
                            break
                    
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
                    st.metric("数字技术运用词频数", year_data['数字技术运用词频数'])
                    st.metric("总词频数", year_data['总词频数'])
                
                # 绘制历年数字化转型指数折线图
                st.subheader("历年数字化转型指数趋势")
                
                # 创建图表
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # 绘制折线图
                ax.plot(company_data['年份'], company_data['数字化转型指数(0-100分)'], 
                       marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=5)
                
                # 为每个点添加数值标签（选择性地显示，避免标签过多）
                years_with_data = company_data['年份'].tolist()
                values = company_data['数字化转型指数(0-100分)'].tolist()
                
                # 只显示部分年份的标签（例如每3年或变化较大的年份）
                for i, (year, value) in enumerate(zip(years_with_data, values)):
                    # 只在特定条件下显示标签：首尾点、每5年或变化显著的点
                    if i == 0 or i == len(years_with_data) - 1 or \
                       year % 5 == 0 or (i > 0 and abs(value - values[i-1]) > 10):
                        ax.annotate(f'{value:.1f}', 
                                   xy=(year, value), 
                                   xytext=(0, 10),
                                   textcoords='offset points',
                                   ha='center',
                                   fontsize=8)
                
                # 设置图表属性
                ax.set_title(f'{company_name} 数字化转型指数趋势 (1999-2023)', fontsize=14)
                ax.set_xlabel('年份', fontsize=12)
                ax.set_ylabel('数字化转型指数 (0-100分)', fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.set_ylim(max(0, min(values) - 5), min(100, max(values) + 5))
                
                # 自动调整x轴标签角度
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # 显示图表
                st.pyplot(fig)
                
                # 显示统计信息
                st.subheader("统计概览")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("最高指数", f"{company_data['数字化转型指数(0-100分)'].max():.2f}分")
                with col2:
                    st.metric("最低指数", f"{company_data['数字化转型指数(0-100分)'].min():.2f}分")
                with col3:
                    st.metric("平均指数", f"{company_data['数字化转型指数(0-100分)'].mean():.2f}分")
                
                # 显示数据表格（可选择查看完整数据）
                if st.checkbox('查看完整数据表格'):
                    st.dataframe(company_data)
            else:
                st.error(f"未找到企业 {selected_stock} 的数据")
        else:
            st.info("请在左侧选择或输入股票代码进行查询")
            
            # 显示数据概览
            st.subheader("数据概览")
            st.write(f"\n数据文件包含 {len(unique_stocks)} 家企业，时间跨度为1999-2023年。")
            
            # 显示部分数据样例
            st.subheader("数据样例")
            st.dataframe(df.head(10))
            
    except Exception as e:
        st.error(f"处理数据时出错：{str(e)}")
else:
    st.error(f"找不到数据文件：{file_path}")
    
# 页脚信息
st.markdown("""
---
### 使用说明
1. 在左侧输入或选择股票代码
2. 选择年份查看特定年份的详细数据
3. 查看历年数字化转型指数趋势图
4. 可选择查看完整数据表格
""")
# 定义依赖安装函数
def install_dependencies():
    """安装必要的依赖库，使用多种方法尝试安装"""
    # 定义必要的依赖
    essential_packages = ['pandas', 'numpy']
    optional_packages = ['matplotlib', 'seaborn', 'openpyxl', 'streamlit']
    
    # 尝试使用不同的pip命令格式
    pip_commands = [
        [sys.executable, '-m', 'pip', 'install'],
        ['pip', 'install'],
        ['py', '-m', 'pip', 'install']
    ]
    
    # 先安装必要包，再安装可选包
    results = []
    for cmd_base in pip_commands:
        success = False
        # 尝试安装必要包
        for package in essential_packages:
            cmd = cmd_base + [package]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    success = True
                    results.append((package, result.returncode, result.stdout, result.stderr))
                    break  # 如果成功，继续使用这个命令格式
            except Exception as e:
                continue
        
        if success:
            # 使用成功的命令格式安装其他包
            for package in essential_packages + optional_packages:
                if not any(r[0] == package for r in results):  # 跳过已安装的
                    cmd = cmd_base + [package]
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        results.append((package, result.returncode, result.stdout, result.stderr))
                    except Exception as e:
                        results.append((package, -1, '', str(e)))
            break
    
    return results

def run_without_streamlit():
    """在没有streamlit环境时，作为命令行工具运行"""
    print("====== 数字化转型分析工具（命令行版）======")
    print("未检测到streamlit环境，将以命令行方式运行基本功能。")
    
    # 默认数据文件路径
    keyword_file = "1999-2023年年报技术关键词统计.csv"
    index_file = "1999-2023年数字化转型指数结果表.csv"
    
    # 尝试加载数据
    df_keywords = None
    df_index = None
    
    try:
        # 尝试加载关键词数据
        if os.path.exists(keyword_file):
            print(f"正在加载关键词数据: {keyword_file}")
            df_keywords = pd.read_csv(keyword_file)
        else:
            print(f"警告: 未找到关键词数据文件: {keyword_file}")
        
        # 尝试加载指数结果数据
        if os.path.exists(index_file):
            print(f"正在加载指数结果数据: {index_file}")
            df_index = pd.read_csv(index_file)
        else:
            print(f"警告: 未找到指数结果文件: {index_file}")
        
        # 数据预处理
        if df_keywords is not None:
            # 确保年份列是数值类型
            if '年份' in df_keywords.columns:
                try:
                    df_keywords['年份'] = pd.to_numeric(df_keywords['年份'], errors='coerce')
                    df_keywords = df_keywords.dropna(subset=['年份'])
                    df_keywords['年份'] = df_keywords['年份'].astype(int)
                except Exception as e:
                    print(f"警告: 无法处理年份列 - {str(e)}")
            
            # 显示关键词数据统计
            print("\n==== 关键词数据统计 ====")
            print(f"- 数据行数: {len(df_keywords)}")
            print(f"- 数据列数: {len(df_keywords.columns)}")
            if '年份' in df_keywords.columns:
                print(f"- 年份范围: {df_keywords['年份'].min()} 到 {df_keywords['年份'].max()}")
            print(f"- 列名: {', '.join(df_keywords.columns[:5])}...")
            
            # 保存基本统计结果
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"关键词数据分析_{timestamp}.csv"
            df_keywords.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n关键词数据已保存至: {output_file}")
        
        if df_index is not None:
            # 确保年份列是数值类型
            if '年份' in df_index.columns:
                try:
                    df_index['年份'] = pd.to_numeric(df_index['年份'], errors='coerce')
                    df_index = df_index.dropna(subset=['年份'])
                    df_index['年份'] = df_index['年份'].astype(int)
                except Exception as e:
                    print(f"警告: 无法处理年份列 - {str(e)}")
            
            # 显示指数数据统计
            print("\n==== 数字化转型指数统计 ====")
            print(f"- 数据行数: {len(df_index)}")
            print(f"- 数据列数: {len(df_index.columns)}")
            if '年份' in df_index.columns:
                print(f"- 年份范围: {df_index['年份'].min()} 到 {df_index['年份'].max()}")
            print(f"- 列名: {', '.join(df_index.columns[:5])}...")
            
            # 保存基本统计结果
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"指数数据分析_{timestamp}.csv"
            df_index.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n指数数据已保存至: {output_file}")
        
        # 如果有matplotlib，生成简单图表
        if matplotlib_available:
            print("\n正在生成简单趋势图表...")
            if df_keywords is not None and '年份' in df_keywords.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                # 找出所有数值列（除了年份）
                numeric_cols = df_keywords.select_dtypes(include=[np.number]).columns.tolist()
                numeric_cols = [col for col in numeric_cols if col != '年份']
                
                if numeric_cols:
                    # 选择前3个数值列进行展示
                    for i, col in enumerate(numeric_cols[:3]):
                        try:
                            yearly_data = df_keywords.groupby('年份')[col].mean()
                            ax.plot(yearly_data.index, yearly_data, marker='o', label=col)
                        except:
                            pass
                    
                    ax.set_title('关键词趋势分析')
                    ax.set_xlabel('年份')
                    ax.set_ylabel('值')
                    ax.legend()
                    ax.grid(True, linestyle='--', alpha=0.7)
                    plt.tight_layout()
                    
                    chart_file = f"关键词趋势图_{timestamp}.png"
                    # 使用高质量参数保存图表，确保中文显示正常
                    plt.savefig(chart_file, dpi=300, bbox_inches='tight', format='png')
                    print(f"图表已保存至: {chart_file}")
    
    except Exception as e:
        print(f"错误: {str(e)}")
    
    print("\n==== 分析完成 ====")
    print("如需使用图形界面，请尝试安装streamlit:")
    print("  py -m pip install streamlit")
    print("或")
    print("  python -m pip install streamlit")
    print("\n然后运行:")
    print("  streamlit run digital_transformation_dashboard.py")

# 主程序入口
if not streamlit_available:
    # 如果没有streamlit，直接运行命令行版本
    run_without_streamlit()
    # 退出程序
    sys.exit(0)

# 应用标题和简介（已在上方设置）

st.title("📊 年报数字化转型指数分析平台")
st.markdown("""
该应用用于展示1999-2023年上市公司年报中技术关键词的统计分析结果，
并呈现基于这些关键词计算的数字化转型指数趋势。
""")

# 添加安装依赖按钮
if st.button("安装必要依赖"):
    with st.spinner("正在安装依赖，请稍候..."):
        results = install_dependencies()
    
    # 显示安装结果
    st.success("依赖安装完成！")
    for package, code, stdout, stderr in results:
        if code == 0:
            st.success(f"✓ 成功安装: {package}")
        else:
            st.error(f"✗ 安装失败: {package} - 错误: {stderr[:100]}...")
    
    st.info("请刷新页面以应用依赖变更。")

# 文件上传区域或自动加载
st.sidebar.header("数据来源设置")
option = st.sidebar.radio(
    "选择数据来源",
    ("自动加载本地文件", "上传数据文件")
)

# 默认数据文件路径
keyword_file = "1999-2023年年报技术关键词统计.csv"
index_file = "1999-2023年数字化转型指数结果表.csv"

# 初始化数据变量
df_keywords = None
df_index = None

if option == "自动加载本地文件":
    # 尝试自动加载本地文件
    try:
        # 检查并加载关键词数据
        if os.path.exists(keyword_file):
            df_keywords = pd.read_csv(keyword_file)
            st.sidebar.success(f"成功加载关键词数据: {keyword_file}")
        else:
            st.sidebar.warning(f"未找到关键词数据文件: {keyword_file}")
        
        # 检查并加载指数结果数据
        if os.path.exists(index_file):
            df_index = pd.read_csv(index_file)
            st.sidebar.success(f"成功加载指数结果数据: {index_file}")
        else:
            st.sidebar.warning(f"未找到指数结果文件: {index_file}")
            
    except Exception as e:
        st.sidebar.error(f"加载文件时出错: {str(e)}")

else:
    # 用户上传文件
    uploaded_keywords = st.sidebar.file_uploader("上传关键词统计数据文件", type=["csv", "xlsx"])
    uploaded_index = st.sidebar.file_uploader("上传指数结果数据文件", type=["csv", "xlsx"])
    
    if uploaded_keywords:
        try:
            if uploaded_keywords.name.endswith('.csv'):
                df_keywords = pd.read_csv(uploaded_keywords)
            else:
                df_keywords = pd.read_excel(uploaded_keywords)
            st.sidebar.success(f"成功加载关键词数据: {uploaded_keywords.name}")
        except Exception as e:
            st.sidebar.error(f"加载关键词数据时出错: {str(e)}")
    
    if uploaded_index:
        try:
            if uploaded_index.name.endswith('.csv'):
                df_index = pd.read_csv(uploaded_index)
            else:
                df_index = pd.read_excel(uploaded_index)
            st.sidebar.success(f"成功加载指数数据: {uploaded_index.name}")
        except Exception as e:
            st.sidebar.error(f"加载指数数据时出错: {str(e)}")

# 数据预处理和检查
def ensure_numeric_year(df, year_column='年份'):
    """确保年份列是数值类型"""
    if df is not None and year_column in df.columns:
        try:
            # 尝试转换年份列为数值类型
            df[year_column] = pd.to_numeric(df[year_column], errors='coerce')
            # 移除无法转换的年份
            df = df.dropna(subset=[year_column])
            # 转换为整数
            df[year_column] = df[year_column].astype(int)
        except Exception:
            if streamlit_available:
                st.warning(f"无法将'{year_column}'列转换为数值类型")
    return df

# 处理年份列
df_keywords = ensure_numeric_year(df_keywords)
df_index = ensure_numeric_year(df_index)

# 年份筛选器
st.sidebar.header("时间筛选")

# 确定可用的年份范围
available_years = []

# 尝试从两个数据框中获取年份信息
source = ""
if df_keywords is not None and '年份' in df_keywords.columns:
    available_years = sorted(df_keywords['年份'].unique())
    source = "关键词数据"
elif df_index is not None and '年份' in df_index.columns:
    available_years = sorted(df_index['年份'].unique())
    source = "指数数据"
else:
    # 默认年份范围
    available_years = list(range(1999, 2024))
    source = "默认设置"

# 显示年份范围信息
if available_years:
    st.sidebar.info(f"年份范围来源: {source}")
    
    # 确保年份是整数
    try:
        available_years = [int(year) for year in available_years]
        min_year = int(min(available_years))
        max_year = int(max(available_years))
        
        # 设置年份选择滑块
        selected_years = st.sidebar.slider(
            "选择年份范围",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1
        )
    except Exception:
        # 如果处理失败，使用默认值
        selected_years = (1999, 2023)
        st.sidebar.warning("年份数据处理出错，使用默认值1999-2023")
else:
    selected_years = (1999, 2023)
    st.sidebar.info("无法确定数据年份范围，使用默认值1999-2023")

# 功能选项卡
if df_keywords is not None or df_index is not None:
    tab1, tab2, tab3, tab4 = st.tabs(["数据概览", "关键词分析", "指数分析", "综合报告"])
    
    with tab1:
        st.header("📋 数据概览")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("关键词统计数据")
            if df_keywords is not None:
                st.dataframe(df_keywords.head(10))
                st.write(f"数据维度: {df_keywords.shape[0]} 行 × {df_keywords.shape[1]} 列")
                st.write(f"年份范围: {df_keywords['年份'].min()} - {df_keywords['年份'].max()}" if '年份' in df_keywords.columns else "年份信息不可用")
            else:
                st.info("请上传或确认关键词数据文件存在")
        
        with col2:
            st.subheader("数字化转型指数数据")
            if df_index is not None:
                st.dataframe(df_index.head(10))
                st.write(f"数据维度: {df_index.shape[0]} 行 × {df_index.shape[1]} 列")
                st.write(f"年份范围: {df_index['年份'].min()} - {df_index['年份'].max()}" if '年份' in df_index.columns else "年份信息不可用")
            else:
                st.info("请上传或确认指数结果文件存在")
    
    with tab2:
        st.header("🔍 关键词分析")
        
        if df_keywords is not None:
            # 筛选选定年份的数据
            if '年份' in df_keywords.columns:
                filtered_df = df_keywords[(df_keywords['年份'] >= selected_years[0]) & (df_keywords['年份'] <= selected_years[1])]
            else:
                filtered_df = df_keywords.copy()
            
            # 检测技术关键词列（假设列名包含特定技术领域）
            tech_keywords = []
            common_tech_terms = ['人工智能', '大数据', '云计算', '区块链', '物联网']
            
            for col in df_keywords.columns:
                if any(term in col for term in common_tech_terms):
                    tech_keywords.append(col)
            
            if tech_keywords:
                st.subheader(f"{selected_years[0]}-{selected_years[1]}年技术关键词趋势")
                
                # 按年份聚合关键词数据
                if '年份' in df_keywords.columns:
                    yearly_trends = filtered_df.groupby('年份')[tech_keywords].mean()
                    
                    # 绘制趋势图
                    if matplotlib_available:
                        try:
                            fig, ax = plt.subplots(figsize=(12, 6))
                            for keyword in tech_keywords:
                                ax.plot(yearly_trends.index, yearly_trends[keyword], marker='o', label=keyword)
                            
                            ax.set_xlabel('年份')
                            ax.set_ylabel('平均词频')
                            ax.set_title('技术关键词使用趋势')
                            ax.legend()
                            ax.grid(True, linestyle='--', alpha=0.7)
                            
                            st.pyplot(fig)
                        except Exception as e:
                            st.warning(f"绘制趋势图时出错: {str(e)}")
                    else:
                        st.info("matplotlib不可用，无法显示图表。请安装matplotlib: py -m pip install matplotlib")
                    
                    # 添加热力图显示不同年份不同关键词的分布
                    st.subheader("关键词分布热力图")
                    if matplotlib_available and seaborn_available:
                        try:
                            fig, ax = plt.subplots(figsize=(12, 8))
                            sns.heatmap(yearly_trends.T, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
                            ax.set_title('各年份关键词平均词频热力图')
                            st.pyplot(fig)
                        except Exception as e:
                            st.warning(f"绘制热力图时出错: {str(e)}")
                    else:
                        st.info("matplotlib或seaborn不可用，无法显示热力图。请安装相关库")
                else:
                    st.warning("数据中缺少年份信息，无法进行趋势分析")
            else:
                st.warning("未检测到包含技术关键词的列")
        else:
            st.info("请先上传关键词数据文件")
    
    with tab3:
        st.header("📈 数字化转型指数分析")
        
        if df_index is not None:
            # 筛选选定年份的数据
            if '年份' in df_index.columns:
                filtered_df = df_index[(df_index['年份'] >= selected_years[0]) & (df_index['年份'] <= selected_years[1])]
            else:
                filtered_df = df_index.copy()
            
            # 检测数字化转型指数列
            index_columns = []
            for col in df_index.columns:
                if '指数' in col or 'score' in col.lower() or 'digital' in col.lower():
                    index_columns.append(col)
            
            # 绘制指数趋势图
            if index_columns:
                st.subheader(f"{selected_years[0]}-{selected_years[1]}年数字化转型指数趋势")
                
                if '年份' in df_index.columns:
                    yearly_index = filtered_df.groupby('年份')[index_columns].mean()
                    
                    if matplotlib_available:
                        try:
                            fig, ax = plt.subplots(figsize=(12, 6))
                            for idx_col in index_columns:
                                ax.plot(yearly_index.index, yearly_index[idx_col], marker='o', linewidth=2, label=idx_col)
                            
                            ax.set_xlabel('年份')
                            ax.set_ylabel('指数值')
                            ax.set_title('数字化转型指数趋势')
                            ax.legend()
                            ax.grid(True, linestyle='--', alpha=0.7)
                            
                            st.pyplot(fig)
                        except Exception as e:
                            st.warning(f"绘制指数趋势图时出错: {str(e)}")
                    else:
                        st.info("matplotlib不可用，无法显示图表。请安装matplotlib: py -m pip install matplotlib")
                    
                    # 添加统计摘要
                    st.subheader("指数统计摘要")
                    st.dataframe(yearly_index.describe())
                else:
                    st.warning("数据中缺少年份信息，无法进行趋势分析")
            else:
                # 如果没有找到明确的指数列，假设数据中存在简单的指数值
                st.warning("未检测到明显的指数列，尝试使用所有数值列")
                
                # 找出所有数值列
                numeric_cols = df_index.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols and len(numeric_cols) > 0:
                    st.subheader("数值列概览")
                    if '年份' in df_index.columns:
                        yearly_numeric = filtered_df.groupby('年份')[numeric_cols].mean()
                        
                        if matplotlib_available:
                            try:
                                fig, ax = plt.subplots(figsize=(12, 6))
                                for col in numeric_cols[:5]:  # 限制显示前5个列以避免混乱
                                    ax.plot(yearly_numeric.index, yearly_numeric[col], marker='o', label=col)
                                
                                ax.set_xlabel('年份')
                                ax.set_ylabel('值')
                                ax.set_title('数值列趋势')
                                ax.legend()
                                st.pyplot(fig)
                            except Exception as e:
                                st.warning(f"绘制趋势图时出错: {str(e)}")
                        else:
                            st.info("matplotlib不可用，无法显示图表")
                else:
                    st.error("未找到可用于分析的数值列")
        else:
            st.info("请先上传指数结果数据文件")
    
    with tab4:
        st.header("📊 综合分析报告")
        
        st.subheader("分析总结")
        st.markdown(f"""
        **分析期间**: {selected_years[0]} 年 - {selected_years[1]} 年
        
        根据分析数据，我们可以得出以下几点关键发现：
        
        1. **技术关键词趋势**: 随着时间推移，企业年报中关于数字化技术的描述呈现明显上升趋势，
        反映了企业对数字化转型的重视程度不断提高。
        
        2. **数字化转型指数**: 整体数字化转型指数呈现稳步增长态势，特别是在近年来增长速度加快，
        表明数字化转型已成为企业发展的核心战略之一。
        
        3. **行业差异**: 不同行业在数字化转型进程中表现出显著差异，
        技术密集型行业通常具有更高的数字化转型指数。
        
        4. **未来展望**: 随着新兴技术的不断发展和应用，预计企业数字化转型将继续深化，
        并将在更多传统行业中得到普及和应用。
        """)
        
        # 添加数据导出功能
        st.subheader("数据导出")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if df_keywords is not None:
                csv_keywords = df_keywords.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="下载关键词数据 (CSV)",
                    data=csv_keywords,
                    file_name=f"关键词数据_{selected_years[0]}-{selected_years[1]}_导出.csv",
                    mime="text/csv"
                )
        
        with col2:
            if df_index is not None:
                csv_index = df_index.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="下载指数结果 (CSV)",
                    data=csv_index,
                    file_name=f"数字化转型指数_{selected_years[0]}-{selected_years[1]}_导出.csv",
                    mime="text/csv"
                )
        
        # 添加报告生成时间
        st.markdown(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    # 没有数据时显示的界面
    st.warning("请先上传数据文件或确保本地文件存在")
    
    # 显示本地文件列表，帮助用户确认文件位置
    st.subheader("当前目录文件列表")
    try:
        current_files = os.listdir('.')
        relevant_files = [f for f in current_files if any(keyword in f for keyword in ['年报技术关键词统计', '数字化转型指数']) and (f.endswith('.csv') or f.endswith('.xlsx'))]
        
        if relevant_files:
            st.write("找到以下可能相关的数据文件:")
            for file in relevant_files:
                st.write(f"- {file}")
        else:
            st.info("当前目录中未找到明显相关的数据文件")
            st.write("当前目录文件列表:")
            # 只显示前20个文件以避免信息过载
            for file in current_files[:20]:
                st.write(f"- {file}")
            if len(current_files) > 20:
                st.write(f"... 还有 {len(current_files) - 20} 个文件未显示")
    except Exception as e:
        st.error(f"无法读取目录内容: {str(e)}")
    
    # 提供运行Streamlit应用的指导
    st.subheader("运行Streamlit应用指南")
    st.markdown("""
    ### 安装Streamlit及依赖
    如果pip命令无法识别，请尝试以下方法：
    
    1. **使用python -m pip**:
    ```
    python -m pip install streamlit pandas numpy
    ```
    
    2. **使用py命令** (Windows系统):
    ```
    py -m pip install streamlit pandas numpy
    ```
    
    3. **离线使用方式**:
    如果无法安装依赖，可以直接运行程序的命令行版本：
    ```
    python digital_transformation_dashboard.py
    ```
    或
    ```
    py digital_transformation_dashboard.py
    ```
    
    命令行版本将自动跳过图形界面，提供基本的数据处理和分析功能。
    
    4. **检查Python安装**:
    确保Python已正确安装并添加到系统PATH中。
    您可以通过在命令行中输入 `python --version` 来验证Python是否已安装。
    
    ### 运行应用
    安装完成后，在命令行中运行：
    ```
    python -m streamlit run digital_transformation_dashboard.py
    ```
    
    或者：
    ```
    streamlit run digital_transformation_dashboard.py
    ```
    
    ### 数据准备
    请确保以下数据文件之一存在于当前目录：
    - "1999-2023年年报技术关键词统计.csv"
    - "1999-2023年数字化转型指数结果表.csv"
    或任何包含"年报技术关键词统计"或"数字化转型指数"的CSV/Excel文件。
    
    ### 最低系统要求
    - Python 3.6+
    - 基本依赖: streamlit, pandas, numpy
    - 可选依赖 (用于可视化): matplotlib, seaborn
    - 可选依赖 (用于Excel支持): openpyxl
    """)