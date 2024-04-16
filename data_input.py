import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# 데이터 파일 경로
DATA_FILE = "sales_data.csv"

# 데이터 불러오기
data = pd.read_csv(DATA_FILE)
data['Date'] = pd.to_datetime(data['Date'])  # 날짜 형식으로 변환

with st.form("data_input"):
    date = st.date_input("매출 날짜")
    project = st.radio("프로젝트명", options=["게임", "굿즈", "패스트 컨설팅", "잔여티켓 플랫폼", "Kindle 전자책"])
    revenue = st.number_input("매출 금액 (원)", min_value=0, step=1000)
    submit = st.form_submit_button("추가")

    if submit and revenue and project:
        new_row = pd.DataFrame({'Date': [date], 'Project': [project], 'Sales': [int(revenue)]})
        data = pd.concat([data, new_row], ignore_index=True)
        data['Date'] = pd.to_datetime(data['Date'])  # 날짜 형식으로 변환
        data = data.sort_values('Date')  # 날짜를 기준으로 데이터 정렬
        data.to_csv(DATA_FILE, index=False)  # 정렬된 데이터를 CSV 파일에 저장
        st.success(f"최신 업데이트 값: 날짜 - {date}, 프로젝트명 - {project}, 매출 금액 - {revenue:,} 원")
        st.experimental_rerun()

# 데이터 저장
data.to_csv(DATA_FILE, index=False)

# 전체 매출 및 목표 설정
total_target = 100000000  # 1억원
total_sales = data['Sales'].sum()

# 메트릭 컬럼 설정
col1, col2, col3 = st.columns(3)

# 메트릭으로 전체 매출 및 목표 금액 표시
with col1:
    st.metric("목표 금액", f"{total_target:,.0f}원")
with col2:
    st.metric("전체 매출", f"{total_sales:,.0f}원")
with col3:
   progress = total_sales / total_target
   st.metric("달성률", f"{progress:.2%}")

# # 달성률 프로그레스 바와 텍스트 표시
# with col3:
#     progress = total_sales / total_target
#     progress_bar = st.progress(progress)
#     st.write(f"달성률: {progress:.1%}")

# # 실제 달성률에 따라 프로그레스 바 업데이트
# for percent_complete in range(int(progress * 100) + 1):
#     time.sleep(0.02)  # 애니메이션 속도 조절 (0.5초마다 업데이트)
#     progress_bar.progress(percent_complete / 100)
