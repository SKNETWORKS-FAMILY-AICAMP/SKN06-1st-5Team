import streamlit as st
import pandas as pd
import numpy as np


st.title("전기차 충전소")
df = pd.read_csv('EV_merged3.csv')

show_checkbox = st.checkbox("충전소 차트가 보고싶은 자 여기로..")

if show_checkbox:
    st.write("음...충분히 강해진 듯하군..")
    st.write("충전소명, 충전소 위치 및 운영기관별 비회원가, 회원가 등을 나타내는 목록입니다.")
    st.dataframe(df)  # Same as st.write(df)


show_checkbox2 = st.checkbox("그래프가 필요한 자 여기로..")

if show_checkbox2: 
    st.write("여기선 지역별로 충전소의 개수를 파악하거나 회원가와 비회원가의 차이를 비교할수있지..")

    st.image('./graph1.png') 
    st.markdown("<h5 style='text-align: center;'>지역별 충전소의 개수</h5>", unsafe_allow_html=True)
    st.image('./graph2.png')
    st.markdown("<h5 style='text-align: center;'>지역별 전기차 충전가 평균</h5>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center;'>--남색 : 회원가/ 주황색 : 비회원가</h5>", unsafe_allow_html=True)
    st.image('./graph3.png') 
    st.markdown("<h5 style='text-align: center;'>회원가/비회원가의 평균 가격 차이</h5>", unsafe_allow_html=True)
    



show_checkbox3 = st.checkbox("지도가 필요한 자 여기로..")

if show_checkbox3:
    st.write("전국의 전기차 충전소 위치가 한눈에 보이는구나..")
    st.map(data=df, latitude='위도', longitude='경도', color=None, size=None, zoom=None, use_container_width=True, width=None, height=None)
    # df = pd.DataFrame(
    #     {
    #         "col1": 
    #         "col2": 
    #         "col3": 
    #         "col4": 
    #     }
    # )


st.image('./darklord.png', caption=100, width=200,)