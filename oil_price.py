import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 폰트
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은고딕
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# Streamlit 제목
st.title('지역별 평균 유가 추이 및 증감 분석')

#파일 경로
file_paths = {
    "경유": "C:/Users/Playdata/Desktop/class/SKN06-1st-5Team/주유소_지역별_평균판매가격(경유).csv",
    "보통 휘발유": "C:/Users/Playdata/Desktop/class/SKN06-1st-5Team/주유소_지역별_평균판매가격(보통).csv",
    "등유": "C:/Users/Playdata/Desktop/class/SKN06-1st-5Team/주유소_지역별_평균판매가격(등유).csv",
    "고급 휘발유": "C:/Users/Playdata/Desktop/class/SKN06-1st-5Team/주유소_지역별_평균판매가격(고급).csv"
}

# CSV 데이터 로드 함수
@st.cache_data 
def load_data(file_path):
    df = pd.read_csv(file_path, encoding='euc-kr')
    df['연도'] = df['구분'].str[:4]  # '구분' 열에서 연도 추출
    df['월'] = df['구분'].str[5:7]  # '구분' 열에서 월 추출
    return df

# 사용자가 연로종류 선택
selected_file = st.selectbox("연료 종류 선택", options=list(file_paths.keys()))
df = load_data(file_paths[selected_file])

# 사용자가 월 선택
selected_month = st.selectbox('조회할 월 선택', list(range(1, 13)), format_func=lambda x: f"{x}월")
selected_month_str = f"{selected_month:02d}" 
df_month = df[df['월'] == selected_month_str]

# 연도별 특정 월평균 가격
average_prices_month = df_month.groupby('연도').mean(numeric_only=True)
# 연도별 증감 가격
average_prices_month_diff = average_prices_month.diff().dropna()  # 전년 대비 증감 계산 (NaN 값 제거)

#그래프 색상
colors = {
    '서울': 'blue',
    '부산': 'orange',
    '대구': 'green',
    '인천': 'red',
    '광주': 'purple',
    '대전': 'brown',
    '울산': 'pink',
    '경기': 'gray',
    '강원': 'cyan',
    '충북': 'magenta',
    '충남': 'yellow',
    '전북': 'teal',
    '전남': 'navy',
    '경북': 'olive',
    '경남': 'gold',
    '제주': 'lime',
    '세종': 'coral'
}

plt.figure(figsize=(12, 6))
for column in average_prices_month.columns:
    if column in colors:
        plt.plot(average_prices_month.index, average_prices_month[column], marker='o', color=colors[column], label=column)

plt.title(f'{selected_file} 지역별 평균 가격 ({selected_month}월)', fontsize=16)
plt.xlabel('연도', fontsize=14)
plt.ylabel('평균 가격(₩)', fontsize=14)
plt.legend()
plt.xticks(rotation=45)
plt.grid()

st.pyplot(plt)

# 증감 계산 결과를 표로 출력 (Markdown 형식)
st.subheader(f'{selected_month}월 전년도 대비 증감(₩)')

table_style = """
<style>
table {
    font-size: 12px;
    width: 80%;
    margin: 0 auto;
}
thead th { background-color: #f0f0f0; }
tbody td { text-align: center; }
</style>
"""

diff_table_md = average_prices_month_diff.style.format("{:.2f}").to_html()
st.markdown(table_style + diff_table_md, unsafe_allow_html=True)