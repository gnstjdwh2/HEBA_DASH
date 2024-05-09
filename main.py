import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import date, datetime

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

# 도넛 차트 색상 매핑
COLOR_MAP = {
    'blue': ['#29b5e8', '#155F7A'],
    'green': ['#27AE60', '#12783D'],
    'orange': ['#F39C12', '#875A12'],
    'red': ['#E74C3C', '#781F16']
}

# 페이지 설정
st.set_page_config(
    page_title='HEBA 대시보드',
    layout='wide',
    initial_sidebar_state='expanded'
)

alt.themes.enable("dark")

# Streamlit 앱 디자인 수정
st.markdown(f"""
    <style>
        .st-subheader {{
            font-size: 5px !important;
        }}
        .reportview-container {{
            background-color: {color_scheme['background']};
            color: {color_scheme['text']};
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

# 사이드바 넓이를 20%로 고정
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 100%;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 100%;
        margin-left: -20%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# D-day 설정
due_date = date(2024, 8, 31)
today = date.today()

# 남은 일수 계산
days_left = (due_date - today).days - 1 # 배포 시 하루 추가 되있어서 -1

# CSS 스타일 정의
css = """
<style>
.st-info {
    background-color: #0E1117;
    color: #fff;
    border: none;
    border-radius: 15px;
    padding: 15px;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease;
    margin-bottom: 20px;
}

.st-info:hover {
    transform: scale(1.05);
}

.st-info .icon {
    font-size: 28px;
    margin-bottom: 5px;
}
</style>
"""

# CSS 스타일 적용
st.markdown(css, unsafe_allow_html=True)

# 사이드바 레이아웃 조정
with st.sidebar:
    # D-day 출력
    st.sidebar.markdown(f"""
    <div class="st-info">
        <strong>D-{days_left}</strong>
    </div>
    """, unsafe_allow_html=True)
        
# 전체 매출 및 목표
total_sales = data['Sales Amount'].sum()
total_target = 100000000  # 1억원


# 달성률 사이드바
with st.sidebar:
    # 데이터 처리
    df_project_sales = data.groupby('Team')['Sales Amount'].sum().sort_values(ascending=False)
    df_project_profit = data.groupby('Team')['Profit Amount'].sum().sort_values(ascending=False)
    df_project_sales_rank = df_project_sales.reset_index()
    df_project_profit_rank = df_project_profit.reset_index()
    df_project_rank = pd.merge(df_project_sales_rank, df_project_profit_rank, on='Team')

    # 매출 달성 목표액 및 수익 달성 목표액 설정
    sales_target = 100000000  # 1억
    profit_target = 25000000  # 2500만원

    # 총 매출액 및 총 수익액 계산
    total_sales = df_project_rank['Sales Amount'].sum()
    total_profit = df_project_rank['Profit Amount'].sum()

    # 매출 달성률 및 수익 달성률 계산
    sales_achievement_rate = round((total_sales / sales_target) * 100)
    profit_achievement_rate = round((total_profit / profit_target) * 100)

    # 도넛 차트 생성 함수
    def make_donut(input_response, input_text, input_color):
        color_map = {
            'blue': ['#29b5e8', '#155F7A'],
            'green': ['#27AE60', '#12783D'],
            'orange': ['#F39C12', '#875A12'],
            'red': ['#E74C3C', '#781F16']
        }
        chart_color = color_map.get(input_color, ['#29b5e8', '#155F7A'])  # 기본값은 'blue'

        source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100 - input_response, input_response]
        })
        source_bg = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100, 0]
        })

        plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
            theta="% value",
            color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None),
        ).properties(width=110, height=140)

        text = plot.mark_text(align='center', color=chart_color[0], font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(
            text=alt.value(f'{input_response:.0f} %')
        )

        plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
            theta="% value",
            color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None)
        ).properties(width=110, height=140)

        return plot_bg + plot + text

    donut_chart_sales = make_donut(sales_achievement_rate, '매출 달성률', 'blue')
    donut_chart_profit = make_donut(profit_achievement_rate, '수익 달성률', 'orange')

    achievement_col = st.columns(2)
    with achievement_col[0]:
        st.info(f'매출 \n\n {total_sales:,.0f} ₩')
        st.altair_chart(donut_chart_sales)
    with achievement_col[1]:
        st.info(f'수익 ({(total_profit / total_sales):.2%})\n\n{total_profit:,.0f} ₩')
        st.altair_chart(donut_chart_profit)

# 사이드바 생성
start_date = st.sidebar.date_input("시작 날짜", value=data['Date'].min())
end_date = st.sidebar.date_input("종료 날짜", value=data['Date'].max())

    # 필터링된 데이터
filtered_data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]

with st.sidebar.expander("매출 / 수익 정보 입력", expanded=False):
    # 날짜 입력
    date = st.date_input("날짜", value=datetime.today())
    
    # 팀 선택
    team = st.selectbox("팀", ["게임", "굿즈", "패스트 컨설팅", "잔여티켓 플랫폼", "Kindle 전자책"])
    
    # 매출 생성자 입력
    sales_person = st.text_input("매출 생성자")
    
    # 매출 금액 입력
    sales_amount_str = st.text_input("매출 금액", value="0")
    
    # 수익 금액 입력
    profit_amount_str = st.text_input("수익 금액", value="0")
    
    if st.button("입력"):
        if sales_amount_str != "0":
            # 입력된 문자열을 숫자로 변환
            try:
                sales_amount = float(sales_amount_str)
                profit_amount = float(profit_amount_str)
                
                # 입력된 데이터를 데이터프레임에 추가
                new_data = pd.DataFrame({
                    "Date": [date],
                    "Team": [team],
                    "Sales Person": [sales_person],
                    "Sales Amount": [sales_amount],
                    "Profit Amount": [profit_amount]
                })
                data = pd.concat([data, new_data], ignore_index=True)
                
                # 날짜별로 정렬
                data["Date"] = pd.to_datetime(data["Date"])
                data = data.sort_values("Date")
                
                # CSV 파일에 저장
                data.to_csv(DATA_FILE, index=False)
                
                current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
                # 가장 최근에 입력한 데이터 내용 출력
                st.success(f"입력 완료\n"
                        f"\n날짜: {current_datetime}\n"
                        f"\n팀: {team}\n"
                        f"\n매출 생성자: {sales_person}\n"
                        f"\n매출 금액: {sales_amount}\n"
                        f"\n수익 금액: {profit_amount}\n")

                # 입력란 초기화
                sales_person = ""
                sales_amount_str = ""
                profit_amount_str = ""
                
                st.experimental_rerun()
            except ValueError:
                st.error("매출 금액과 수익 금액은 숫자로 입력해주세요.")
        else:
            st.warning("매출액은 필수 입니다.")

## section layout 조절
col1, col2 = st.columns(2)

with col1:
    # 프로젝트별 매출 현황
    df_project_sales = data.groupby('Team')['Sales Amount'].sum().sort_values(ascending=False)
    df_project_profit = data.groupby('Team')['Profit Amount'].sum().sort_values(ascending=False)

    # 팀별 매출 및 수익 데이터
    df_team_sales_profit = filtered_data.groupby('Team').agg({'Sales Amount': 'sum', 'Profit Amount': 'sum'}).reset_index()

    # 매출 1등 팀과 수익 1등 팀 찾기
    max_sales_team = df_team_sales_profit.loc[df_team_sales_profit['Sales Amount'].idxmax(), 'Team']
    max_profit_team = df_team_sales_profit.loc[df_team_sales_profit['Profit Amount'].idxmax(), 'Team']

    # 매출 막대 색상 설정
    sales_colors = ['#29b5e8' if team == max_sales_team else '#155F7A' for team in df_team_sales_profit['Team']]

    # 수익 막대 색상 설정
    profit_colors = ['#F39C12' if team == max_profit_team else '#875A12' for team in df_team_sales_profit['Team']]

    # 혼합 막대 그래프 생성
    fig_sales_profit_by_project = go.Figure(data=[
        go.Bar(
            name='매출',
            x=df_team_sales_profit['Team'],
            y=df_team_sales_profit['Sales Amount'],
            marker_color=sales_colors,
            opacity=0.7
        ),
        go.Bar(
            name='수익',
            x=df_team_sales_profit['Team'],
            y=df_team_sales_profit['Profit Amount'],
            marker_color=profit_colors,
            opacity=0.7
        )
    ])

    # 그래프 레이아웃 설정
    fig_sales_profit_by_project.update_layout(
        title='팀별 매출 및 수익',
        xaxis_title='',
        yaxis_title='',
        barmode='group',
        legend=dict(x=0.8, y=1, orientation='v'),
        plot_bgcolor=color_scheme['background'],
        paper_bgcolor=color_scheme['background'],
        font=dict(color=color_scheme['text']),
        height=300
    )

    st.plotly_chart(fig_sales_profit_by_project, use_container_width=True)

    team_data = filtered_data.groupby('Team').agg({'Sales Amount': 'sum', 'Profit Amount': 'sum'})
    team_data['Profit Margin'] = team_data['Profit Amount'] / team_data['Sales Amount']

    # 팀별 수익률 표시
    fig = px.bar(team_data, x=team_data.index, y='Profit Margin', title='팀별 수익률', text_auto='.2%')
    fig.update_layout(xaxis_title='', yaxis_title='', height=300,
                    yaxis=dict(tickmode='array', tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                ticktext=['0%', '20%', '40%', '60%', '80%', '100%']))

    # 차트 색상 설정
    fig.update_traces(marker_color=['#27AE60' if pm >= 0.5 else '#12783D' for pm in team_data['Profit Margin']])

    st.plotly_chart(fig, use_container_width=True)

## 주차별 매출
# 주차 계산을 위해 'Date' 열을 datetime으로 변환
data = filtered_data.copy()  # filtered_data를 복사하여 사용
data['Date'] = pd.to_datetime(data['Date'])

# 월과 주차 열 추가
data['Month'] = data['Date'].dt.month
data['Week'] = data['Date'].dt.isocalendar().week

# 월별 주차 계산
data['MonthWeek'] = data.groupby(['Month'])['Week'].rank(method='dense').astype(int)
data['MonthWeek'] = data['Month'].astype(str) + 'W' + data['MonthWeek'].astype(str)

# 주차별 매출 총액 계산
weekly_sales = data.groupby(['MonthWeek'])['Sales Amount'].sum().reset_index()

# 주차별 팀별 매출 총액 계산
team_weekly_sales = data.groupby(['MonthWeek', 'Team'])['Sales Amount'].sum().reset_index()

# 그래프 생성
fig = go.Figure()

# x축 레이블 순서 고정을 위한 배열 생성
x_labels = weekly_sales['MonthWeek']

# 막대 그래프 추가
fig.add_trace(go.Bar(x=weekly_sales['MonthWeek'], y=weekly_sales['Sales Amount'], name='전체 매출', marker_color='rgba(220, 220, 220, 0.8)'))

# 팀별 선 그래프 추가
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
for i, team in enumerate(team_weekly_sales['Team'].unique()):
    team_data = team_weekly_sales[team_weekly_sales['Team'] == team]
    fig.add_trace(go.Scatter(x=team_data['MonthWeek'], y=team_data['Sales Amount'], name=team, mode='lines+markers', marker=dict(color=colors[i % len(colors)])))

# 그래프 레이아웃 설정
fig.update_layout(
    title='주차별 매출',
    xaxis_title='',
    yaxis_title='',
    legend_title='',
    hovermode='x unified',
    xaxis=dict(categoryarray=x_labels)  # x축 레이블 순서 고정
)

# Streamlit에 그래프 표시
st.plotly_chart(fig, use_container_width=True)

with col2:
    # 팀별 매출 합계 계산
    team_sales = filtered_data.groupby('Team')['Sales Amount'].sum().reset_index()
    # 팀별 수익 합계 계산
    team_profit = filtered_data.groupby('Team')['Profit Amount'].sum().reset_index()

    # 파이 차트 데이터 생성
    fig = go.Figure(data=[
        go.Pie(
            name='수익',
            labels=team_profit['Team'],
            values=team_profit['Profit Amount'],
            marker=dict(colors=px.colors.cyclical.IceFire, line=dict(color='black', width=0.3)),  # 색상 팔레트 변경
            # hovertext=[f"수익: {profit:,.0f}" for team, profit in zip(team_profit['Team'], team_profit['Profit Amount'])],
            textinfo='none',
            hole=0.4  # 수익 차트를 안쪽 원으로 설정
        ),
        go.Pie(
            name='매출',
            labels=team_sales['Team'],
            values=team_sales['Sales Amount'],
            marker=dict(colors=px.colors.cyclical.IceFire, line=dict(color='black', width=0.3)),  # 색상 팔레트 변경
            # hovertext=[f"매출: {sales:,.0f}" for team, sales in zip(team_sales['Team'], team_sales['Sales Amount'])],
            textinfo='none',
            hole=0.7  # 매출 차트를 바깥 원으로 설정
        )
    ])

    # 차트 레이아웃 설정
    fig.update_layout(
        title='팀별 매출 및 수익 비중',
        height=585,
        font=dict(color=color_scheme['text']),
        plot_bgcolor=color_scheme['background'],
        paper_bgcolor=color_scheme['background'],
        legend=dict(orientation='h', xanchor='center', x=0.5, y=-0.1)
    )

    # 차트 렌더링
    st.plotly_chart(fig, use_container_width=True)

with st.expander('팀 / 개인 성과 순위', expanded=False):
    df_project_sales_rank = df_project_sales.reset_index()
    df_project_profit_rank = df_project_profit.reset_index()
    df_project_sales_rank.columns = ['Team', 'Sales Amount']
    df_project_profit_rank.columns = ['Team', 'Profit Amount']
    df_project_rank = pd.merge(df_project_sales_rank, df_project_profit_rank, on='Team')
    df_project_rank['Sales Rank'] = df_project_rank['Sales Amount'].rank(ascending=False).astype(int)
    df_project_rank['Profit Rank'] = df_project_rank['Profit Amount'].rank(ascending=False).astype(int)

    team_ranking_col1, team_ranking_col2 = st.columns([2, 1])  # 열 너비 비율 조정

    with team_ranking_col1:
        st.dataframe(df_project_rank, column_order=("Team", "Sales Amount", "Sales Rank", "Profit Amount", "Profit Rank"), hide_index=True, width=None, column_config={
            "Team": st.column_config.TextColumn("팀"),
            "Sales Amount": st.column_config.ProgressColumn("매출", format="%f", min_value=0, max_value=max(df_project_rank['Sales Amount'])),
            "Sales Rank": st.column_config.TextColumn("순위"),
            "Profit Amount": st.column_config.ProgressColumn("수익", format="%f", min_value=0, max_value=max(df_project_rank['Profit Amount'])),
            "Profit Rank": st.column_config.TextColumn("순위")
        })

    st.info('Progress Bar 우측값 = 누적액')

    # 개인별 매출 기여 순위 TOP 5
    individual_sales = data.groupby('Sales Person')['Sales Amount'].sum().reset_index().sort_values('Sales Amount', ascending=False).head(5)
    individual_sales.columns = ['이름', '매출']
    # individual_sales['순위'] = individual_sales['매출'].rank(ascending=False, method='dense').astype(int)

    with team_ranking_col2:
        st.dataframe(individual_sales, column_order=('이름', '매출'), hide_index=True, width=None, column_config={
            "이름": st.column_config.TextColumn("이름"),
            "매출": st.column_config.ProgressColumn("매출", format="%f", min_value=0, max_value=max(individual_sales['매출'])),
            # "순위": st.column_config.TextColumn("순위")
        })