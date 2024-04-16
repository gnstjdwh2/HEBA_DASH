import streamlit as st
import pandas as pd
import plotly.express as px
# from streamlit_lottie import st_lottie
# import requests
import time

# 프로젝트 매출 데이터 불러오기
df = pd.read_csv('sales_data.csv')
df['Date'] = pd.to_datetime(df['Date'])  # 날짜 형식으로 변환

# 전체 매출 및 목표
total_sales = df['Sales'].sum()
total_target = 100000000  # 1억원

# 다크 모드 색상 설정
color_scheme = {
    'background': '#0E1117',
    'text': '#FFFFFF',
    'accent': '#1F77B4',
    'accent_negative': '#D62728'
}

# Streamlit 앱 디자인 수정
st.markdown(f"""
    <style>
        .reportview-container {{
            background-color: {color_scheme['background']};
            color: {color_scheme['text']};
        }}
        .metric {{
            color: {color_scheme['accent']};
        }}
        .sidebar .sidebar-content {{
            background-color: {color_scheme['background']};
        }}
        .sidebar .sidebar-content .sidebar-header {{
            color: {color_scheme['text']};
        }}
        .sidebar .sidebar-content .sidebar-options label {{
            color: {color_scheme['text']};
        }}
    </style>
""", unsafe_allow_html=True)

# 사이드바
st.sidebar.title('설정')
st.sidebar.subheader('표시 옵션')
show_sales_by_project = st.sidebar.checkbox('프로젝트별 매출 현황 표시', value=True)
show_sales_proportion = st.sidebar.checkbox('프로젝트 별 매출 비중 표시', value=True)
show_sales_details = st.sidebar.checkbox('프로젝트 별 매출 상세 정보 표시', value=True)
show_sales_ranking = st.sidebar.checkbox('프로젝트 별 매출 순위 표시', value=True)

# 프로젝트별 매출 현황
if show_sales_by_project:
    # st.markdown("---")

    st.subheader('프로젝트별 매출 현황')
    df_project_sales = df.groupby('Project')['Sales'].sum().sort_values(ascending=False)
    fig = px.bar(df_project_sales, x=df_project_sales.index, y=df_project_sales.values, labels={'x': 'Project', 'y': 'Sales'})
    fig.update_layout(
        title='Sales by Project',
        xaxis_title='Project',
        yaxis_title='Sales',
        plot_bgcolor=color_scheme['background'],
        paper_bgcolor=color_scheme['background'],
        font=dict(color=color_scheme['text'])
    )
    st.plotly_chart(fig, use_container_width=True)

# 프로젝트 별 매출 비중
if show_sales_proportion:
    st.markdown("---")

    st.subheader('매출 비중')
    df_project_sales = df.groupby('Project')['Sales'].sum()
    fig = px.pie(df_project_sales, values=df_project_sales.values, names=df_project_sales.index)
    fig.update_layout(
        title='Sales Proportion by Project',
        plot_bgcolor=color_scheme['background'],
        paper_bgcolor=color_scheme['background'],
        font=dict(color=color_scheme['text']),
        width=800,  # 차트 너비 설정
        height=500  # 차트 높이 설정
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=False)  # use_container_width를 False로 설정


# 프로젝트 별 매출 순위
if show_sales_ranking:
    st.markdown("---")

    st.subheader('매출 순위')
    df_project_sales = df.groupby('Project')['Sales'].sum().sort_values(ascending=False)
    df_project_sales = pd.DataFrame({'Project': df_project_sales.index, 'Sales': df_project_sales.values})
    df_project_sales['Rank'] = range(1, len(df_project_sales) + 1)
    df_project_sales['Sales'] = df_project_sales['Sales'].apply(lambda x: f"{x:,}")  # 숫자 형식 변경
    st.write(
        f"""
        <div style="text-align: center;">
            <table style="margin: 0 auto; width: 100%; border-collapse: collapse;">  <!-- 테이블 너비 설정 -->
                <thead>
                    <tr style="background-color: #1f77b4; color: white;">
                        <th style="text-align: center;">Rank</th>
                        <th style="text-align: center;">Project</th>
                        <th style="text-align: center;">Sales</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td style="text-align: center;">{row["Rank"]}</td><td style="text-align: center;">{row["Project"]}</td><td style="text-align: center;">{row["Sales"]} 원</td></tr>' for _, row in df_project_sales.iterrows()])}
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

# 프로젝트 별 매출 상세 정보
if show_sales_details:
    st.markdown("---")

    st.subheader('매출 상세 정보')
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # 날짜 형식 변경
    df['Sales'] = df['Sales'].apply(lambda x: f"{x:,}")  # 숫자 형식 변경
    
    # Streamlit 테이블 스타일 설정
    st.write(
        f"""
        <div style="text-align: center;">
            <table style="margin: 0 auto; width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #1f77b4; color: white;">
                        <th style="text-align: center; padding: 8px; border: 1px solid white;">Date</th>
                        <th style="text-align: center; padding: 8px; border: 1px solid white;">Project</th>
                        <th style="text-align: center; padding: 8px; border: 1px solid white;">Sales</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td style="text-align: center; padding: 8px; border: 1px solid #ccc;">{row["Date"]}</td><td style="text-align: center; padding: 8px; border: 1px solid #ccc;">{row["Project"]}</td><td style="text-align: center; padding: 8px; border: 1px solid #ccc;">{row["Sales"]} 원</td></tr>' for _, row in df.iterrows()])}
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )
