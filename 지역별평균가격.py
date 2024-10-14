import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# Streamlit 앱 제목
st.title('Fuel Average Prices by Region')

# 파일 경로 설정
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

# 지역 이름 영어 변경 매핑
region_mapping = {
    '서울': 'Seoul',
    '부산': 'Busan',
    '대구': 'Daegu',
    '인천': 'Incheon',
    '광주': 'Gwangju',
    '대전': 'Daejeon',
    '울산': 'Ulsan',
    '경기': 'Gyeonggi',
    '강원': 'Gangwon',
    '충북': 'Chungbuk',
    '충남': 'Chungnam',
    '전북': 'Jeonbuk',
    '전남': 'Jeonnam',
    '경북': 'Gyeongbuk',
    '경남': 'Gyeongnam',
    '제주': 'Jeju',
    '세종': 'Sejong'
}

# 사용자가 선택할 수 있도록 파일 목록 제공
selected_file = st.selectbox("연료 종류 선택", options=list(file_paths.keys()))

# 파일 경로에 따라 데이터 로드
df = load_data(file_paths[selected_file])

# 사용자가 조회할 연도와 월을 선택할 수 있도록 인터페이스 제공
selected_month = st.selectbox('조회할 월 선택', list(range(1, 13)), format_func=lambda x: f"{x}월")
selected_month_str = f"{selected_month:02d}"  # 선택한 월을 두 자리로 변환

# 특정 월에 해당하는 데이터 필터링
df_month = df[df['월'] == selected_month_str]

# 연도별 특정 월의 평균 가격 계산
average_prices_month = df_month.groupby('연도').mean(numeric_only=True)

# 데이터프레임의 컬럼을 영어로 변환
average_prices_month.columns = average_prices_month.columns.map(region_mapping)
average_prices_month = average_prices_month.loc[:, average_prices_month.columns.notnull()]  # NaN 값 제거

# 그래프 색상 설정
colors = {
    'Seoul': 'blue',
    'Busan': 'orange',
    'Daegu': 'green',
    'Incheon': 'red',
    'Gwangju': 'purple',
    'Daejeon': 'brown',
    'Ulsan': 'pink',
    'Gyeonggi': 'gray',
    'Gangwon': 'cyan',
    'Chungbuk': 'magenta',
    'Chungnam': 'yellow',
    'Jeonbuk': 'teal',
    'Jeonnam': 'navy',
    'Gyeongbuk': 'olive',
    'Gyeongnam': 'gold',
    'Jeju': 'lime',
    'Sejong': 'coral'
}

# 그래프 그리기
plt.figure(figsize=(12, 6))
for column in average_prices_month.columns:
    if column in colors:  # 색상 딕셔너리에 있는 경우만 그리기
        plt.plot(average_prices_month.index, average_prices_month[column], marker='o', color=colors[column], label=column)

plt.title(f'{selected_file} 지역별 평균 가격 ({selected_month}월)', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Average Price (₩)', fontsize=14)
plt.legend()
plt.xticks(rotation=45)
plt.grid()

# Streamlit에 그래프 표시
st.pyplot(plt)
