# streamlit run ./SKN06-1st-5Team/mainpage.py
import streamlit as st

st.set_page_config(
    page_title="mainpage",
    page_icon="🚗",
    layout="wide"
)
st.title("🚗전국 주유소 유가 및 전기차 충전소 가격 조회 시스템🚗")
st.write("이 시스템은 전국 주유소와 전기차 충전소의 가격 정보를 비교할 수 있습니다. 분산된 정보를 한 곳에 제공함으로써 사용자들이 최저가 주유소와 충전소를 손쉽게 찾을 수 있습니다. 이를 통해 소비자들이 합리적인 가격으로 연료를 공급받을 수 있도록 돕고, 전기차 충전 관련 정보를 쉽게 접근할 수 있는 편의성을 제공하고자 합니다.")

st.write("더 자세한 내용은 아래 사이트를 참조하세요.")
tabs = st.tabs(["주유소", "전기차 충전소"])
with tabs[0]:
    st.page_link("https://www.opinet.co.kr/user/main/mainView.do", label="싼 주유소 찾기_오피넷", icon="⛽")
    st.image("./image/3.png", use_column_width=True)

with tabs[1]:
    st.page_link("https://www.chargekorea.com/charge/index.php", label="전기차 충전소 찾기", icon="⚡")
    st.image("./image/2.png", use_column_width=True)
    
    st.page_link("https://ev.or.kr/nportal/main.do#", label="무공해차 통합누리집", icon="🔋")
    st.image("./image/1.png", use_column_width=True)