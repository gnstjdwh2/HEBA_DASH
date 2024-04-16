import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# 데이터 파일 경로
DATA_FILE = "sales_data.csv"

# 데이터 불러오기
data = pd.read_csv(DATA_FILE)
data['Date'] = pd.to_datetime(data['Date'])  # 날짜 형식으로 변환

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

# 사이드바 생성
st.sidebar.title("필터링 옵션")
start_date = st.sidebar.date_input("시작 날짜", value=data['Date'].min())
end_date = st.sidebar.date_input("종료 날짜", value=data['Date'].max())

# 필터링된 데이터
filtered_data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]

# 매출 달성률 계산
target_revenue = 100000000  # 1억 매출 목표
actual_revenue = filtered_data['Sales'].sum()
revenue_attainment = (actual_revenue / target_revenue) * 100

# st.markdown("---")  # 구분선 추가

# 날짜별 매출 추이 그래프
st.subheader("📈 날짜별 매출")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=filtered_data['Date'].dt.strftime('%Y-%m-%d'),
    y=filtered_data['Sales'],
    name='Sales',
    marker=dict(color=filtered_data['Sales'], colorscale='Viridis')
))
fig.update_layout(
    scene=dict(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Sales'),
        zaxis=dict(title='Project', type='category', categoryorder='array', categoryarray=filtered_data['Project'].unique())
    ),
    title='Sales Trend by Date',
    plot_bgcolor=color_scheme['background'],
    paper_bgcolor=color_scheme['background'],
    font=dict(color=color_scheme['text'])
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")  # 구분선 추가

# 매출 달성률 정보
st.subheader("📊 매출 달성률")
fig = go.Figure(data=[go.Pie(labels=['실제 매출', '남은 목표'], values=[actual_revenue, target_revenue - actual_revenue], marker=dict(colors=[color_scheme['accent'], color_scheme['accent_negative']]))])
fig.update_layout(
    title=f'매출 달성률: {revenue_attainment:.2f}%',
    plot_bgcolor=color_scheme['background'],
    paper_bgcolor=color_scheme['background'],
    font=dict(color=color_scheme['text'])
)
st.plotly_chart(fig, use_container_width=True)

st.write(f"목표 매출: {target_revenue:,} 원")
st.write(f"실제 매출: {actual_revenue:,} 원")
st.write(f"데이터 기준일: {filtered_data['Date'].max().strftime('%Y-%m-%d')}")