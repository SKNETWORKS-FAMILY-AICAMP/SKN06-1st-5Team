# streamlit run ./SKN06-1st-5Team/pages/oil.py
# streamlit run ./pages/oil.py
import json
import pymysql
import requests
import numpy as np
import pandas as pd
import streamlit as st
import configparser as parser
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
props = parser.ConfigParser()
props.read("./config.ini")
conf = props

def search_csv(a, b, c, standard):  # 조건 데이터 조회_csv
    df = pd.read_csv("./oil_data.csv", encoding='cp949')
    if b is None:  # 전국
        if c != "전체":
            df = df[df['셀프'] == c]
    elif b == "전체":  # 도만 선택
        df = df[df['시도'] == a]
        if c != "전체":
            df = df[df['셀프'] == c]
    else:  # 시도 및 시군구 선택
        df = df[(df['시도'] == a) & (df['시군구'] == b)]
        if c != "전체":
            df = df[df['셀프'] == c]

    df = df.sort_values(by=standard)
    df.index = pd.RangeIndex(start=1, stop=len(df) + 1, step=1)
    return df

def search(a, b, c, standard):  # 조건 데이터 조회_mysql
    with pymysql.connect(host=conf['MYSQL']['host'], port=3306, user=conf['MYSQL']['user'], password=conf['MYSQL']['password'], db=conf['MYSQL']['db']) as conn:
        with conn.cursor() as cur:
            if b is None:  # 전국
                if c == "전체":
                    sql = f"SELECT * FROM oil_data WHERE {standard} IS NOT NULL ORDER BY {standard}"
                    cur.execute(sql)
                else:
                    sql = f"SELECT * FROM oil_data WHERE 셀프 = %s AND {standard} IS NOT NULL ORDER BY {standard}"
                    cur.execute(sql, (c,))
                    
            elif b == "전체":  # 도만 선택
                if c == "전체":
                    sql = f"SELECT * FROM oil_data WHERE 시도 = %s AND {standard} IS NOT NULL ORDER BY {standard}"
                    cur.execute(sql, (a,))
                else:
                    sql = f"SELECT * FROM oil_data WHERE 시도 = %s AND 셀프 = %s AND {standard} IS NOT NULL ORDER BY {standard}"
                    cur.execute(sql, (a, c))
            else:  # 시도 및 시군구 선택
                if c == "전체":
                    sql = f"SELECT * FROM oil_data WHERE 시도 = %s AND 시군구 = %s AND {standard} IS NOT NULL ORDER BY {standard}"
                    cur.execute(sql, (a, b))
                else:
                    sql = f"SELECT * FROM oil_data WHERE 시도 = %s AND 시군구 = %s AND 셀프 = %s AND {standard} IS NOT NULL ORDER BY {standard}"
                    cur.execute(sql, (a, b, c))
            
            cell = cur.fetchall()
    
    columns = ['시도', '시군구', '이름', '셀프', '주소', '번호', '고급휘발유', '보통휘발유', '경유', '실내등유']
    data = list(cell)  # 쿼리 결과로 데이터 배열 생성
    df = pd.DataFrame(data, columns=columns)
    df.index = pd.RangeIndex(start=1, stop=len(df) + 1, step=1)
    return df

def plot():  # 메인 함수
    a, b, c, btn = sidebar()
    
    st.markdown("<style> .large-font { font-size:24px !important; margin-bottom: -90px !important; } </style>", unsafe_allow_html=True)
    st.markdown('<p class="large-font">정렬 기준</p>', unsafe_allow_html=True)
    standard = st.radio("", ["이름", "고급휘발유", "보통휘발유", "경유", "실내등유"], horizontal=True)
    
    column = ['시도', '시군구', '이름', '셀프', '주소', '고급휘발유', '보통휘발유', '경유', '실내등유']
    if standard == '이름':
        column_order = ['시도', '시군구', '이름', '셀프', '고급휘발유', '보통휘발유', '경유', '실내등유', '주소', '번호']
    else:
        column_order = ['시도', '시군구', '이름', '셀프']
        column_order.append(standard)
        for col in column[5:]:
            if col != standard and col not in ['주소', '번호']:
                column_order.append(col)
        column_order.extend(['주소', '번호'])
    
    localdf = search(a, b, c, standard) if btn == "MYSQL" else search_csv(a, b, c, standard)
    st.markdown(f"<div style='text-align: left; font-size: 24px;'>{a} {b}(셀프: {c}) 평균</div>" if b else f"<div style='text-align: left; font-size: 24px;'>{a}(셀프: {c}) 평균</div>", unsafe_allow_html=True)
    mean(localdf['고급휘발유'], localdf['보통휘발유'], localdf['경유'], localdf['실내등유'])  # 지역 평균 유가
    
    st.markdown(f"<div style='text-align: left; font-size: 24px;'>{a} {b} {c} 조회 결과({standard} 기준)</div>" if b else f"<div style='text-align: left; font-size: 24px;'>{a} {c} 조회 결과({standard} 기준)</div>", unsafe_allow_html=True)
    event = st.dataframe(localdf, width=1410, hide_index=True, selection_mode="single-row", on_select="rerun", column_order=column_order)
    select = 0
    select = event.selection.rows[0] + 1 if event.selection.rows else select
    
    if select:
        col1, col2 = st.columns(2)
        with col2:
            st.markdown(f"<div style='text-align: left; font-size: 24px;'>{localdf['이름'][select]}</div>", unsafe_allow_html=True)
            oilpricedf(localdf['고급휘발유'][select], localdf['보통휘발유'][select], localdf['경유'][select], localdf['실내등유'][select])

        with col1:
            x, y = getxy(localdf['주소'][select])
            mapplot(localdf['이름'][select], localdf['주소'][select], x, y)
        
        
def oilpricedf(pgasoline, gasoline, diesel, kerosene):
    df = pd.DataFrame({'고급휘발유': [pgasoline], '보통휘발유': [gasoline], '경유': [diesel], '실내등유': [kerosene]})
    st.dataframe(df, width=800, hide_index=True)

def mean(pgasoline, gasoline, diesel, kerosene): # 지역 평균 계산 함수
    pgasoline = pgasoline.replace(0, np.nan).mean()
    gasoline = gasoline.replace(0, np.nan).mean()
    diesel = diesel.replace(0, np.nan).mean()
    kerosene = kerosene.replace(0, np.nan).mean()
    ndf = pd.DataFrame({'고급휘발유': [pgasoline], '보통휘발유': [gasoline], '경유': [diesel], '실내등유': [kerosene]})
    df = st.data_editor(ndf, width=1410, hide_index=True)
    return df

def getxy(addr): # 위도, 경도 구하는 함수 (카카오 api 사용)
    key = conf['KAKAO_API']['key']
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query={}'.format(addr)
    headers = {"Authorization": "KakaoAK " + key}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match = result['documents'][0]
    x = float(match['x'])
    y = float(match['y'])
    return x, y

def mapplot(name, addr, x, y): # 지도 띄우는 함수
    m = folium.Map(location=[y, x], width=800, zoom_start=25) # 서울 위도/경도
    txt = '<div style="text-align: center;">{}: {}</div>'.format(name, addr)
    marker = folium.Marker([y, x], popup=folium.Popup(txt, max_width=500),)
    marker.add_to(m)
    st_folium(m)

def sidebar(): # 사이드 바 함수
    ganggwon = ['강원 강릉시', '강원 고성군', '강원 동해시', '강원 삼척시', '강원 속초시', 
            '강원 양구군', '강원 양양군', '강원 영월군', '강원 원주시', '강원 인제군', 
            '강원 정선군', '강원 철원군', '강원 춘천시', '강원 태백시', '강원 평창군', 
            '강원 홍천군', '강원 화천군', '강원 횡성군']
    gwon = ['전체'] + [i.split(" ")[1] for i in ganggwon if " " in i]

    gyeonggi = ['경기 가평군', '경기 고양시', '경기 고양시덕양구', '경기 고양시일산동구', 
        '경기 고양시일산서구', '경기 과천시', '경기 광명시', '경기 광주시', 
        '경기 구리시', '경기 군포시', '경기 김포시', '경기 남양주시', 
        '경기 동두천시', '경기 부천시', '경기 부천시소사구', '경기 부천시오정구', 
        '경기 부천시원미구', '경기 성남시', '경기 성남시분당구', '경기 성남시수정구', 
        '경기 성남시중원구', '경기 수원시', '경기 수원시권선구', '경기 수원시영통구', 
        '경기 수원시장안구', '경기 수원시팔달구', '경기 시흥시', '경기 안산시', 
        '경기 안산시단원구', '경기 안산시상록구', '경기 안성시', '경기 안양시', 
        '경기 안양시동안구', '경기 안양시만안구', '경기 양주시', '경기 양평군', 
        '경기 여주시', '경기 연천군', '경기 오산시', '경기 용인시', 
        '경기 용인시기흥구', '경기 용인시수지구', '경기 용인시처인구', 
        '경기 의왕시', '경기 의정부시', '경기 이천시', '경기 파주시', 
        '경기 평택시', '경기 포천시', '경기 하남시', '경기 화성시']
    ggi = ['전체'] + [i.split(" ")[1] for i in gyeonggi if " " in i]

    gyeongnam = ['경남 거제시', '경남 거창군', '경남 고성군', '경남 김해시', '경남 남해군', 
            '경남 밀양시', '경남 사천시', '경남 산청군', '경남 양산시', 
            '경남 의령군', '경남 진주시', '경남 창녕군', '경남 창원시', 
            '경남 창원시마산합포구', '경남 창원시마산회원구', '경남 창원시성산구', 
            '경남 창원시의창구', '경남 창원시진해구', '경남 통영시', 
            '경남 하동군', '경남 함안군', '경남 함양군', '경남 합천군']
    gnam = ['전체'] + [i.split(" ")[1] for i in gyeongnam if " " in i]

    gyeongbug = ['경북 경산시', '경북 경주시', '경북 고령군', '경북 구미시', '경북 김천시', 
            '경북 문경시', '경북 봉화군', '경북 상주시', '경북 성주군', 
            '경북 안동시', '경북 영덕군', '경북 영양군', '경북 영주시', 
            '경북 영천시', '경북 예천군', '경북 울릉군', '경북 울진군', 
            '경북 의성군', '경북 청도군', '경북 청송군', '경북 칠곡군', 
            '경북 포항시', '경북 포항시남구', '경북 포항시북구']
    gbug = ['전체'] + [i.split(" ")[1] for i in gyeongbug if " " in i]

    gwangju = ['광주 광산구', '광주 남구', '광주 동구', '광주 북구', '광주 서구']
    gju = ['전체'] + [i.split(" ")[1] for i in gwangju if " " in i]

    daegu = ['대구 군위군', '대구 남구', '대구 달서구', '대구 달성군', '대구 동구', 
            '대구 북구', '대구 서구', '대구 수성구', '대구 중구']
    dgu = ['전체'] + [i.split(" ")[1] for i in daegu if " " in i]

    daejeon = ['대전 대덕구', '대전 동구', '대전 서구', '대전 유성구', '대전 중구']
    djeon = ['전체'] + [i.split(" ")[1] for i in daejeon if " " in i]

    busan = ['부산 강서구', '부산 금정구', '부산 기장군', '부산 남구', '부산 동구', 
                '부산 동래구', '부산 부산진구', '부산 북구', '부산 사상구', 
                '부산 사하구', '부산 서구', '부산 수영구', '부산 연제구', 
                '부산 영도구', '부산 중구', '부산 해운대구']
    bsan = ['전체'] + [i.split(" ")[1] for i in busan if " " in i]

    seoul = ['서울 강남구', '서울 강동구', '서울 강북구', '서울 강서구', '서울 관악구', 
            '서울 광진구', '서울 구로구', '서울 금천구', '서울 노원구', 
            '서울 도봉구', '서울 동대문구', '서울 동작구', '서울 마포구', 
            '서울 서대문구', '서울 서초구', '서울 성동구', '서울 성북구', 
            '서울 송파구', '서울 양천구', '서울 영등포구', '서울 용산구', 
            '서울 은평구', '서울 종로구', '서울 중구', '서울 중랑구']
    sul = ['전체'] + [i.split(" ")[1] for i in seoul if " " in i]

    saejong = ['세종 세종시']
    sjong = ['전체'] + [i.split(" ")[1] for i in saejong if " " in i]

    ulsan = ['울산 남구', '울산 동구', '울산 북구', '울산 울주군', '울산 중구']
    usan = ['전체'] + [i.split(" ")[1] for i in ulsan if " " in i]

    incheon = ['인천 강화군', '인천 계양구', '인천 남동구', '인천 동구', '인천 미추홀구', 
            '인천 부평구', '인천 서구', '인천 연수구', '인천 옹진군', '인천 중구']
    icheon = ['전체'] + [i.split(" ")[1] for i in incheon if " " in i]

    jeonnam = ['전남 강진군', '전남 고흥군', '전남 곡성군', '전남 광양시', '전남 구례군', 
            '전남 나주시', '전남 담양군', '전남 목포시', '전남 무안군', 
            '전남 보성군', '전남 순천시', '전남 신안군', '전남 여수시', 
            '전남 영광군', '전남 영암군', '전남 완도군', '전남 장성군', 
            '전남 장흥군', '전남 진도군', '전남 함평군', '전남 해남군', 
            '전남 화순군']
    jnam = ['전체'] + [i.split(" ")[1] for i in jeonnam if " " in i]

    jeonbug = ['전북 고창군', '전북 군산시', '전북 김제시', '전북 남원시', '전북 무주군', 
            '전북 부안군', '전북 순창군', '전북 완주군', '전북 익산시', 
            '전북 임실군', '전북 장수군', '전북 전주시', '전북 전주시덕진구', 
            '전북 전주시완산구', '전북 정읍시', '전북 진안군']
    jbug = ['전체'] + [i.split(" ")[1] for i in jeonbug if " " in i]

    jju = ['제주 서귀포시', '제주 제주시']
    jeju = ['전체'] + [i.split(" ")[1] for i in jju if " " in i]

    chungnam = ['전체', '충남 계룡시', '충남 공주시', '충남 금산군', '충남 논산시', 
            '충남 당진시', '충남 보령시', '충남 부여군', '충남 서산시', 
            '충남 서천군', '충남 아산시', '충남 예산군', '충남 천안시', 
            '충남 천안시동남구', '충남 천안시서북구', '충남 청양군', 
            '충남 태안군', '충남 홍성군']
    chnam = ['전체'] +  [i.split(" ")[1] for i in chungnam if " " in i]

    chungbug = ['충북 괴산군', '충북 단양군', '충북 보은군', '충북 영동군', 
            '충북 옥천군', '충북 음성군', '충북 제천시', '충북 증평군', 
            '충북 진천군', '충북 청주시', '충북 청주시상당구', 
            '충북 청주시서원구', '충북 청주시청원구', '충북 청주시흥덕구', 
            '충북 충주시']
    chbug = ['전체'] + [i.split(" ")[1] for i in chungbug if " " in i]
    
    btn = st.sidebar.radio("데이터베이스", ["CSV", "MYSQL"], horizontal=True)
    sido = ['전국', '강원', '경기', '경남', '경북', '광주', '대구', '대전', '부산', '서울', '세종', '울산', '인천', '전남', '전북', '제주', '충남', '충북']
    select_sido = st.sidebar.selectbox("시/도", sido)

    if select_sido == '강원':
        sigungu = gwon
    elif select_sido == '경기':
        sigungu = ggi
    elif select_sido == '경남':
        sigungu = gnam
    elif select_sido == '경북':
        sigungu = gbug
    elif select_sido == '광주':
        sigungu = gju
    elif select_sido == '대구':
        sigungu = dgu
    elif select_sido == '대전':
        sigungu = djeon
    elif select_sido == '부산':
        sigungu = bsan
    elif select_sido == '서울':
        sigungu = sul
    elif select_sido == '세종':
        sigungu = sjong
    elif select_sido == '울산':
        sigungu = usan
    elif select_sido == '인천':
        sigungu = icheon
    elif select_sido == '전남':
        sigungu = jnam
    elif select_sido == '전북':
        sigungu = jbug
    elif select_sido == '제주':
        sigungu = jeju
    elif select_sido == '충남':
        sigungu = chnam
    elif select_sido == '충북':
        sigungu = chbug
    elif select_sido == '전국':
        sigungu = None
        
    if sigungu is None:
        select_gu = None
    else:
        select_gu = st.sidebar.selectbox("시/군/구", sigungu)
    
    iself = st.sidebar.selectbox("셀프", ["전체", "Y", "N"])
    return select_sido, select_gu, iself, btn


if __name__ == "__main__":
    plot()