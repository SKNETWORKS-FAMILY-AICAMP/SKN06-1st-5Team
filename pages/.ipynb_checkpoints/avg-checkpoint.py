import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "C:/Windows/Fonts/malgun.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

st.title('지역별 평균 유가 추이 및 증감 분석')
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
    df['연도'] = df['구분'].str[:4]
    df['월'] = df['구분'].str[5:7] 
    return df

# 각 파일을 처리하는 함수
def process_file(file_path):
    df = pd.read_csv(file_path, encoding='euc-kr')
    df['연도'] = df['구분'].str[:4]
    average_prices = df.groupby('연도').mean(numeric_only=True)
    return average_prices

# 사용자가 연료 종류 선택
selected_file = st.selectbox("연료 종류 선택", options=list(file_paths.keys()))
df = load_data(file_paths[selected_file])

st.sidebar.write(f"{selected_file}의 연도별 평균 가격")
avg_prices = round(process_file(file_paths[selected_file]),2)
st.sidebar.dataframe(avg_prices)

# 사용자가 월 선택
selected_month = st.selectbox('조회할 월 선택', list(range(1, 13)), format_func=lambda x: f"{x}월")
selected_month_str = f"{selected_month:02d}" 
df_month = df[df['월'] == selected_month_str]

# 계산식
average_prices_month = df_month.groupby('연도').mean(numeric_only=True) # 연도별 특정 월 평균 가격
average_prices_month_diff = round(average_prices_month.diff().dropna(),2)       # 연도별 증감 가격, 첫 번째 연도 차이는 NaN이므로 제거

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

plt.title(f'{selected_file} 지역별 평균 가격 ({selected_month}월)', fontsize=19)
plt.xlabel('연도', fontsize=14)
plt.ylabel('평균 가격(₩)', fontsize=14)
plt.legend()
plt.xticks(rotation=45)
plt.grid()
st.pyplot(plt)

st.markdown(f"##### {selected_month}월 전년도 대비 증감(₩)")
st.dataframe(average_prices_month_diff)