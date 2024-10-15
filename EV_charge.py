import streamlit as st
import pandas as pd
import numpy as np


st.title("전기차 충전소")
st.write("충전소 위치 별 가격 목록 입니다.")
df = pd.read_csv('EV_merged2.csv')

st.dataframe(df)  # Same as st.write(df)
st.bar_chart(data=df, x='지역명', y='비회원가', x_label='지역명', y_label='비회원가', color=None, horizontal=False, stack=None, width=None, height=None, use_container_width=True)


st.bar_chart(data=df, x='지역명', y='회원가', x_label='지역명', y_label='회원가', color=None, horizontal=False, stack=None, width=None, height=None, use_container_width=True)


st.write("충전소 위치 별 가격 목록 입니다.")
st.map(data=df, latitude='위도', longitude='경도', color=None, size=None, zoom=None, use_container_width=True, width=None, height=None)
# df = pd.DataFrame(
#     {
#         "col1": 
#         "col2": 
#         "col3": 
#         "col4": 
#     }
# )