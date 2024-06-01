import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import date, datetime
import hmac
from ipyvizzu import Chart, Data, Config, Style, DisplayTarget
from streamlit.components.v1 import html
from ipyvizzustory import Story, Slide, Step
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 데이터 파일 경로
DATA_FILE = "sales_data.csv"

# 데이터 불러오기
data = pd.read_csv(DATA_FILE)
data['Date'] = pd.to_datetime(data['Date'])
data['Sales Amount'] = data['Sales Amount'].astype(float)
data['Profit Amount'] = data['Profit Amount'].astype(float)

# 다크 모드 색상 설정
color_scheme = {
    # 'background': '#0E1117',
    'background' : 'white',
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

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        # Return True if the password is validated.
        if st.session_state.get("password_correct", False):
            return True

        # Show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        if "password_correct" in st.session_state:
            st.error("비밀번호를 확인해주세요 😕")
        return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


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
        .story {{
            background-color: #0E1117
            width: auto;
            height: 480px;
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
  background-color: #E3F2FD;
  color: #0D47A1;
  border: 2px solid #2196F3;
  border-radius: 15px;
  padding: 15px;
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 20px;
}

.st-info:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.st-info .icon {
  font-size: 28px;
  margin-bottom: 5px;
  color: #2196F3;
}

.st-info .dday {
  color: #FF5722;
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
total_target = 100000000.0  # 1억

# 달성률 사이드바
with st.sidebar:
    # 데이터 처리
    df_project_sales = data.groupby('Team')['Sales Amount'].sum().sort_values(ascending=False)
    df_project_profit = data.groupby('Team')['Profit Amount'].sum().sort_values(ascending=False)
    df_project_sales_rank = df_project_sales.reset_index()
    df_project_profit_rank = df_project_profit.reset_index()
    df_project_rank = pd.merge(df_project_sales_rank, df_project_profit_rank, on='Team')

    # 매출 달성 목표액 및 수익 달성 목표액 설정
    sales_target = 100000000.0 # 1억
    profit_target = 25000000.0 # 2500만

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

with st.sidebar.expander("매출 / 비용 정보 입력", expanded=False):
    # 날짜 입력
    date_value = st.date_input("날짜", value=datetime.today())
    
    # 팀 선택
    team = st.selectbox("팀", ["게임", "굿즈", "두드림", "HEBA", "Shift", "전자책", "축제"])
    
    # 매출 생성자 선택
    if team == "게임":
        sales_person = st.selectbox("매출 생성자", ["없음", "김다원", "김준혁", "이준석", "최윤영"])
    elif team == "굿즈":
        sales_person = st.selectbox("매출 생성자", ["없음", "김선목", "김채영"])
    elif team == "두드림":
        sales_person = st.selectbox("매출 생성자", ["없음", "민경환", "송시원", "임정희"])
    elif team == "HEBA":
        sales_person = st.selectbox("매출 생성자", ["없음"])
    elif team == "Shift":
        sales_person = st.selectbox("매출 생성자", ["없음", "김문기", "박은채", "서정욱"])
    elif team == "전자책":
        sales_person = st.selectbox("매출 생성자", ["없음", "박해민", "이송하"])
    else:  # 축제
        sales_person = st.selectbox("매출 생성자", ["없음", "김세연", "김선목", "김채영", "남승현", "민경환", "최윤영"])
    
    # 매출 금액 입력
    sales_amount_str = st.text_input("매출", value="0")

    # 비용 금액 입력
    cost_amount_str = st.text_input("비용", value="0")

    if st.button("입력"):
        # 입력된 문자열을 숫자로 변환
        try:
            sales_amount = float(sales_amount_str)
            cost_amount = float(cost_amount_str)
            
            # 수익 계산
            profit_amount = sales_amount - cost_amount
            
            # 입력된 데이터를 데이터프레임에 추가
            new_data = pd.DataFrame({
                "Date": [date_value],
                "Team": [team],
                "Sales Person": [sales_person],
                "Sales Amount": [sales_amount],
                "Cost Amount": [cost_amount],
                "Profit Amount": [profit_amount]
            })
            data = pd.concat([data, new_data], ignore_index=True)
            
            # 데이터 타입 변환
            data["Sales Amount"] = data["Sales Amount"].astype(float)
            data["Cost Amount"] = data["Cost Amount"].astype(float)
            data["Profit Amount"] = data["Profit Amount"].astype(float)
            
            # 날짜별로 정렬
            data["Date"] = pd.to_datetime(data["Date"])
            data = data.sort_values("Date")
            
            # CSV 파일에 저장
            data.to_csv(DATA_FILE, index=False)

            st.rerun()
                
        except ValueError:
            st.error("매출 금액과 비용 금액은 숫자로 입력해주세요.")


data_key_json = {"Date" : "날짜", "Team" : "팀", "Sales Person" : "매출 생성자", "Sales Amount" : "매출", "Profit Amount" : "수익", "Cost Amount" : "비용"}

with st.sidebar.expander("데이터 수정 / 삭제", expanded=False):
    # 날짜 선택
    selected_date = st.date_input("날짜 선택", value=None, min_value=data["Date"].min(), max_value=data["Date"].max())
    # 팀 선택
    selected_team = st.selectbox("팀 선택", data["Team"].unique().tolist())

    # 선택한 조건에 맞는 데이터 필터링
    if selected_date is not None and selected_team:
        filtered_data_side = data[(data["Date"] == pd.to_datetime(selected_date)) & (data["Team"] == selected_team)]
    elif selected_date is not None:
        filtered_data_side = data[data["Date"] == pd.to_datetime(selected_date)]
    elif selected_team:
        filtered_data_side = data[data["Team"] == selected_team]
    else:
        filtered_data_side = data

    if not filtered_data_side.empty:
        selected_index = st.number_input("수정할 데이터 선택", min_value=0, max_value=len(filtered_data_side) - 1, step=1)
        
        if selected_index < len(filtered_data_side):
            selected_data = filtered_data_side.iloc[selected_index]
            st.write("선택한 데이터:")
            
            # 선택한 데이터의 키를 data_key_json 딕셔너리의 값으로 변경하여 보여줌
            displayed_data = {data_key_json[key]: value for key, value in selected_data.to_dict().items()}
            
            # "Date" 열을 "년-월-일" 형식의 문자열로 변환
            displayed_data["날짜"] = displayed_data["날짜"].strftime("%Y-%m-%d")
            
            st.write(displayed_data)

            # 수정할 열 선택
            columns_to_edit = st.multiselect("수정할 데이터 선택", [data_key_json[col] for col in data.columns if col != 'Team'])
            
            # 수정할 값 입력
            edited_values = {}
            for column in columns_to_edit:
                original_column = list(data_key_json.keys())[list(data_key_json.values()).index(column)]
                current_value = selected_data[original_column]
                
                if column == "날짜":
                    new_value = st.date_input(f"{column} 수정", value=current_value)
                elif column == "팀":
                    new_value = st.selectbox(f"{column} 수정", options=["게임", "굿즈", "두드림", "HEBA", "Shift", "전자책", "축제"], index=["게임", "굿즈", "두드림", "HEBA", "Shift", "전자책", "축제"].index(current_value))
                elif column == "매출 생성자":
                    team = selected_data["Team"]
                    if team == "게임":
                        options = ["없음", "김다원", "김준혁", "이준석", "최윤영"]
                    elif team == "굿즈":
                        options = ["없음", "김선목", "김채영"]
                    elif team == "두드림":
                        options = ["없음", "민경환", "송시원", "임정희"]
                    elif team == "HEBA":
                        options = ["없음"]
                    elif team == "Shift":
                        options = ["없음", "김문기", "박은채", "서정욱"]
                    elif team == "전자책":
                        options = ["없음", "박해민", "이송하"]
                    else:  # 축제
                        options = ["없음", "김세연", "김선목", "김채영", "남승현", "민경환", "최윤영"]
                    new_value = st.selectbox(f"{column} 수정", options=options, index=options.index(current_value))
                else:
                    new_value = st.text_input(f"{column} 수정", value=current_value)
                
                edited_values[original_column] = new_value

            # "수정" "삭제"
            col1, col2 = st.columns(2)

            with col1:
                modify_button = st.button("수정", key="modify_button")

            with col2:
                delete_button = st.button("삭제", key="delete_button")

            # 버튼 스타일 적용
            st.markdown(
                """
                <style>
                div.stButton > button {
                    width: 100%;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            if modify_button:
                # 데이터프레임 업데이트
                for column, value in edited_values.items():
                    data.at[selected_data.name, column] = value

                # CSV 파일에 저장
                data['Date'] = pd.to_datetime(data['Date'])
                data.to_csv(DATA_FILE, index=False)
                st.success("데이터가 수정되었습니다.")
                st.experimental_rerun()

            if delete_button:
                if st.warning("정말로 삭제하시겠습니까?"):
                    # 선택한 데이터와 일치하는 행의 인덱스 찾기
                    index_to_delete = filtered_data_side.index[selected_index]
                    
                    # 인덱스를 사용하여 데이터프레임에서 행 삭제
                    data = data.drop(index=index_to_delete)
                    
                    # CSV 파일에 저장
                    data.to_csv(DATA_FILE, index=False)
                    
                    st.success("데이터가 삭제되었습니다.")
                    st.experimental_rerun()
        else:
            st.warning("유효한 데이터를 선택해주세요.")
    else:
        st.warning("선택한 조건에 맞는 데이터가 없습니다.")

## section layout 조절
col1, col2 = st.columns(2)

with col1:
    # 프로젝트별 매출 현황
    df_project_sales = filtered_data.groupby('Team')['Sales Amount'].sum().sort_values(ascending=False)
    df_project_profit = filtered_data.groupby('Team')['Profit Amount'].sum().sort_values(ascending=False)

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

    # # 팀별 매출 및 수익 데이터
    # df_team_sales_profit = filtered_data.groupby('Team').agg({'Sales Amount': 'sum', 'Profit Amount': 'sum'}).reset_index()

    # # 매출 1등 팀과 수익 1등 팀 찾기
    # max_sales_team = df_team_sales_profit.loc[df_team_sales_profit['Sales Amount'].idxmax(), 'Team']
    # max_profit_team = df_team_sales_profit.loc[df_team_sales_profit['Profit Amount'].idxmax(), 'Team']

    # # 매출 막대 색상 설정
    # sales_colors = ['#29b5e8' if team == max_sales_team else '#155F7A' for team in df_team_sales_profit['Team']]

    # # 수익 막대 색상 설정
    # profit_colors = ['#F39C12' if team == max_profit_team else '#875A12' for team in df_team_sales_profit['Team']]

    # # 혼합 막대 그래프 생성
    # fig_sales_profit_by_project = go.Figure(data=[
    #     go.Bar(
    #         name='매출',
    #         x=df_team_sales_profit['Team'],
    #         y=df_team_sales_profit['Sales Amount'],
    #         marker_color=sales_colors,
    #         opacity=0.7
    #     ),
    #     go.Bar(
    #         name='수익',
    #         x=df_team_sales_profit['Team'],
    #         y=df_team_sales_profit['Profit Amount'],
    #         marker_color=profit_colors,
    #         opacity=0.7
    #     )
    # ])

    # # 그래프 레이아웃 설정
    # fig_sales_profit_by_project.update_layout(
    #     title='팀별 매출 및 수익',
    #     xaxis_title='',
    #     yaxis_title='',
    #     barmode='group',
    #     legend=dict(x=0.8, y=1, orientation='v'),
    #     plot_bgcolor='rgba(255, 255, 255, 0.8)',  # 배경색 설정
    #     paper_bgcolor='rgba(255, 255, 255, 0.8)',  # 배경색 설정
    #     font=dict(color='black'),  # 글자색 설정
    #     height=300,
    #     margin=dict(l=20, r=20, t=40, b=20),  # 그래프 여백 설정
    #     shapes=[  # 그래프 테두리 설정
    #         dict(
    #             type='rect',
    #             xref='paper', yref='paper',
    #             x0=0, y0=0, x1=1, y1=1,
    #             line=dict(color='black', width=1)
    #         )
    #     ]
    # )

    # st.plotly_chart(fig_sales_profit_by_project, use_container_width=True)

    # team_data = filtered_data.groupby('Team').agg({'Sales Amount': 'sum', 'Profit Amount': 'sum'})
    # team_data['Profit Margin'] = team_data['Profit Amount'] / team_data['Sales Amount']

    # # 팀별 수익률 표시
    # fig = px.bar(team_data, x=team_data.index, y='Profit Margin', title='팀별 수익률', text_auto='.2%')
    # fig.update_layout(xaxis_title='', yaxis_title='', height=300,
    #                 yaxis=dict(tickmode='array', tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    #                             ticktext=['0%', '20%', '40%', '60%', '80%', '100%']),
    #                 plot_bgcolor='rgba(255, 255, 255, 0.8)',  # 배경색 설정
    #                 paper_bgcolor='rgba(255, 255, 255, 0.8)',  # 배경색 설정
    #                 font=dict(color='black'),  # 글자색 설정
    #                 margin=dict(l=20, r=20, t=40, b=20),  # 그래프 여백 설정
    #                 shapes=[  # 그래프 테두리 설정
    #                     dict(
    #                         type='rect',
    #                         xref='paper', yref='paper',
    #                         x0=0, y0=0, x1=1, y1=1,
    #                         line=dict(color='black', width=1)
    #                     )
    #                 ]
    # )

    # # 차트 색상 설정
    # fig.update_traces(marker_color=['#27AE60' if pm >= 0.5 else '#12783D' for pm in team_data['Profit Margin']])

    # st.plotly_chart(fig, use_container_width=True)

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
            textinfo='none',
            hole=0.4  # 수익 차트를 안쪽 원으로 설정
        ),
        go.Pie(
            name='매출',
            labels=team_sales['Team'],
            values=team_sales['Sales Amount'],
            marker=dict(colors=px.colors.cyclical.IceFire, line=dict(color='black', width=0.3)),  # 색상 팔레트 변경
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

# 팀별 색상 팔레트 생성
colors = px.colors.qualitative.Set2

# 팀별 선 그래프 추가
for i, team in enumerate(team_weekly_sales['Team'].unique()):
    team_data = team_weekly_sales[team_weekly_sales['Team'] == team]
    fig.add_trace(go.Scatter(x=team_data['MonthWeek'], y=team_data['Sales Amount'], name=team, mode='lines+markers', marker=dict(color=colors[i])))

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

## ipyvizzu and ipyvizzu-story
# 팀별 전체 수익 계산
team_total_profit = filtered_data[filtered_data['Team'] != 'HEBA'].groupby('Team')['Profit Amount'].sum().reset_index()

# 팀별 수익의 30% 계산
team_profit_30_percent = team_total_profit.copy()
team_profit_30_percent['Profit Amount'] = team_profit_30_percent['Profit Amount'] * 0.3

# 팀별 수익의 나머지 70% 계산
team_profit_70_percent = team_total_profit.copy()
team_profit_70_percent['Profit Amount'] = team_profit_70_percent['Profit Amount'] * 0.7

# 수익의 30%의 전체 합계 계산
total_30_percent_profit = team_profit_30_percent['Profit Amount'].sum()

# HEBA 팀의 수익 계산
heba_profit = filtered_data[filtered_data['Team'] == 'HEBA']['Profit Amount'].sum()

# 전체 수익과 30% 수익, 나머지 70% 수익을 나타내는 데이터프레임 생성
result_df = pd.DataFrame({
   'Team': team_total_profit['Team'],
   '팀별 수익': team_total_profit['Profit Amount'],
   '수익의 30%': team_profit_30_percent['Profit Amount'],
   '수익의 70%': team_profit_70_percent['Profit Amount'],
   'HEBA' : heba_profit
})

# 데이터 추가
vizzu_data = Data()
vizzu_data.add_df(result_df)

story = Story(data=vizzu_data)

slide1 = Slide(
   Step(
       Config({
           "channels": {
               "y": {"set": ["팀별 수익"]},
               "x": {"set": ["Team"]},
               "label": {"set": ["팀별 수익"]},
           },
       }),
       Style(
           {
               "legend": {"width" : 100}
           }
       )
   )
)
story.add_slide(slide1)

slide2 = Slide(
   Step(
       Config(
           {
               "channels": {
                   "y": {"set": ["수익의 70%"]},
                   "x": {"set": ["Team"]},
                   "color": {"set": ["Team"]},
                   "label": {"set": ["수익의 70%"]}
               },
           }
       )
   )
)
story.add_slide(slide2)

slide3 = Slide(
   Step(
       Config(
           {
               "channels": {
                   "y": {"set": ["수익의 30%"]},
                   "x": {"set": ["Team"]},
                   "color": {"set": ["Team"]},
                   "label": {"set": ["수익의 30%"]}
               },
           }
       )
   )
)
story.add_slide(slide3)

slide4 = Slide(
   Step(
       Config(
           {
               "color" : "Team", 
               "y":["Team"],
               "channels" : {"x" :{"set": None}}
           }
       )
   )
)
story.add_slide(slide4)

slide5 = Slide(
   Step(
       Config(
           {
               "channels": {
                   "y": {"set": ["HEBA"]},
                   "x": {"set": None},
                   "label": {"set": ["HEBA"]},
               },      
           }
       )
   )
)
story.add_slide(slide5)


# you can set the width and height (CSS style)
story.set_size(width="1000px", height="480px")


# you can export the Story into a html file
story.export_to_html(filename="mystory.html")

# or you can get the html Story as a string
html = story.to_html()
# print(html)

# you can display the Story with the `play` method
story.play()

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
    individual_sales = data[data['Sales Person'] != '없음'].groupby('Sales Person')['Sales Amount'].sum().reset_index().sort_values('Sales Amount', ascending=False).head(5)
    individual_sales.columns = ['이름', '매출']

    with team_ranking_col2:
        st.dataframe(individual_sales, column_order=('이름', '매출'), hide_index=True, width=None, column_config={
            "이름": st.column_config.TextColumn("이름"),
            "매출": st.column_config.ProgressColumn("매출", format="%f", min_value=0, max_value=max(individual_sales['매출'])),
        })