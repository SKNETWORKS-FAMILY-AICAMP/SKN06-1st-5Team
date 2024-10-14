from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymysql
from bs4 import BeautifulSoup as BS

already = set(); oil_list = []
def info(drv, link):
    '''
    시도, 시군구 선택 후 페이지 정보 req에 저장 -> beautifulsoup4으로 파싱
    '''
    drv.execute_script("arguments[0].click();", link)
    time.sleep(1)
    
    req = drv.page_source
    bs = BS(req, 'html.parser')
    name = bs.select_one('#os_nm').text
    iself = "셀프" if bs.select_one('#self_icon') else None
    price = []
    price.append(bs.select_one('#b034_p').text) if bs.select_one('#b034_p').text else price.append(None) # 고급휘발유
    price.append(bs.select_one('#b027_p').text) if bs.select_one('#b027_p').text else price.append(None) # 보통휘발유
    price.append(bs.select_one('#d047_p').text) if bs.select_one('#d047_p').text else price.append(None) # 경유
    price.append(bs.select_one('#c004_p').text) if bs.select_one('#c004_p').text else price.append(None) # 실내등유
    return name, iself, price

def chk(sido, sigungu, name, iself):
    with pymysql.connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''
            SELECT 1 FROM oil_data WHERE 시도 = %s AND 시군구 = %s AND 이름 = %s AND 셀프 = %s 
            ''', (sido, sigungu, name, iself))
            isin = cur.fetchone()
            if isin:
                for i in isin:
                    res = i
            else: res = 0
            return res
        
def create_table():
    """
    MySQL 데이터베이스에 oil_data 테이블이 없으면 생성하는 함수
    """
    conn = pymysql.connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS oil_data (
                시도 VARCHAR(50),
                시군구 VARCHAR(50),
                이름 VARCHAR(100),
                셀프 VARCHAR(10),
                고급휘발유 VARCHAR(10),
                보통휘발유 VARCHAR(10),
                경유 VARCHAR(10),
                실내등유 VARCHAR(10),
                PRIMARY KEY (시도, 시군구, 이름, 셀프, 고급휘발유, 보통휘발유, 경유, 실내등유)
            )
            ''')
        conn.commit()
        print("테이블 생성 완료 또는 이미 존재합니다.")
    finally:
        conn.close()
        
def selection(drv, wait, start_i=1, start_j=1):
    '''
    페이지 내 정보를 가져오는 함수
    '''
    try:
        selectsido = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#SIDO_NM0')))
        name1 = [option.text for option in Select(selectsido).options]

        for i in range(start_i, len(name1)):  # 시/도 항목 개수만큼 반복
            selectsido = Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#SIDO_NM0'))))
            selectsido.select_by_index(i)
            sido = name1[i]
            time.sleep(1)
            
            selectsigungu = Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#SIGUNGU_NM0'))))
            name2 = [option.text for option in selectsigungu.options]
            
            for j in range(start_j if i == start_i else 1, len(name2)):  # 시/군/구 항목 개수만큼 반복
                selectsigungu = Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#SIGUNGU_NM0'))))
                selectsigungu.select_by_index(j)
                sigungu = name2[j]
                time.sleep(1)
                
                addr = f"{sido} {sigungu}"
                
                if addr in already:
                    print(f"{addr} 있으므로 넘어감")
                    continue
                
                btn1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#searRgSelect')))
                btn1.click()
                time.sleep(1)
                
                try:
                    btn2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#os_layer3")))
                    btn2.click()
                    time.sleep(1)

                    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#body3 .rlist")))
                    for el in elements:
                        link = el.find_element(by=By.CSS_SELECTOR, value='a')
                        name, iself, price = info(drv, link)
                        pgasoline, gasoline, diesel, kerosene = price
                        
                        # 중복 확인
                        if chk(sido, sigungu, name, iself):
                            print(f"{name} (중복 데이터), 넘어감")
                            continue
                        
                        else:
                            dic = {
                                "시도": sido, "시군구": sigungu, 
                                "이름": name, "셀프": iself, "고급휘발유": pgasoline, 
                                "보통휘발유": gasoline, "경유": diesel, "실내등유": kerosene
                            }
                            print(dic)
                            oil_list.append(dic)
                            
                            # 데이터베이스에 저장
                            with pymysql.connect() as conn:
                                with conn.cursor() as cur:
                                    cur.execute('''
                                    INSERT INTO oil_data (시도, 시군구, 이름, 셀프, 고급휘발유, 보통휘발유, 경유, 실내등유)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ''', (sido, sigungu, name, iself, pgasoline, gasoline, diesel, kerosene))
                                    conn.commit()
                            
                    already.add(addr)
                        
                except Exception as e:
                    print(f"refresh 분기점2: {e}")
                    drv.refresh()
                    # 재시작 시, i와 j를 1로 설정하여 초기화
                    return selection(drv, wait, 1, 1)
                
                print(f"{sigungu} {len(elements)}회 종료")
                
        print(f"{sido} 종료")

    except Exception as e:
        print(f"refresh 분기점1: {e}")
        drv.refresh()
        # 재시작 시, i와 j를 1로 설정하여 초기화
        return selection(drv, wait, 1, 1)
    
    return oil_list

def drv():
    '''
    드라이버 객체 생성
    '''
    create_table() # db 테이블 생성 여부 확인
    drv = webdriver.Chrome()
    wait = WebDriverWait(drv, 20)
    drv.get("https://www.opinet.co.kr/searRgSelect.do")
    selection(drv, wait)
    drv.close()
    
if __name__ == "__main__":
    drv()