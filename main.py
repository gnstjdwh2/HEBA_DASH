import streamlit as st

# 페이지 이동 메뉴 생성
pages = {
    "매출 입력": "data_input.py",
    "Home": "app.py",
    "Page 1": "page1.py"
}

# 사이드바에 페이지 이동 메뉴 추가
selected_page = st.sidebar.radio("Select a page", list(pages.keys()))

# 선택된 페이지에 따라 해당 페이지 파일 실행
page_file = pages[selected_page]
exec(open(page_file).read())