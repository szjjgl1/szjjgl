# 企业数字化转型指数查询系统

## 项目简介

基于1999-2023年数据，通过股票代码查询企业数字化转型指数及历史趋势的Web应用。

## 技术栈

- Python 3.8+
- Streamlit
- Pandas
- Matplotlib
- Plotly

## 在新电脑上运行项目

### 1. 克隆GitHub仓库

```bash
git clone https://github.com/szjjgl1/szjjgl.git
cd szjjgl
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run digital_transformation_dashboard.py
```

### 4. 访问应用

在浏览器中打开 http://localhost:8501

## 项目文件说明

- `digital_transformation_dashboard.py`: 主应用文件
- `1999-2023年数字化转型指数结果表.csv`: 数字化转型指数数据
- `requirements.txt`: 项目依赖列表
- `GIT使用指南.md`: Git使用说明
- `Streamlit Cloud 部署指南.md`: Streamlit Cloud部署说明

## 在线访问

项目已部署在Streamlit Cloud：
[企业数字化转型指数查询系统](https://your-app-url.streamlit.app)

## 数据来源

1999-2023年上市公司年报技术关键词统计数据
